from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QIcon, QFont, QImage, QPixmap
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
import sys
import cv2
import os
import time
from datetime import datetime
from backend import translate_text, recognize_speech
import easyocr
from langdetect import detect, LangDetectException

# Initialize EasyOCR
reader = easyocr.Reader(['en', 'tl'])

# Language code mapping
language_code_map = {
    "English": "en",
    "Tagalog": "tl",
    "Cebuano": "ceb",
    "Ilocano": "ilo"
}

# Word-based heuristic for Cebuano and Ilocano detection
cebuano_words = {"maayong", "daghang", "salamat", "tabangan", "wala", "kabalo" "asa" "pasidaan"}
ilocano_words = {"naimbag", "bigat", "malem", "rabii", "agyamanak", "wen"}

def detect_cebuano_ilocano(text):
    """Custom detection for Cebuano and Ilocano based on common words."""
    words = set(text.lower().split())
    if words & cebuano_words:
        return "ceb"
    elif words & ilocano_words:
        return "ilo"
    return None  # Use langdetect as fallback

class TextTranslateApp(QWidget):
    def __init__(self, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Translate Interface')
        self.setGeometry(50, 50, 1024, 600)

        mainLayout = QVBoxLayout()

        self.backButton = QPushButton(self)
        self.backButton.setIcon(QIcon('./assets/back.png'))
        self.backButton.setFixedSize(50, 50)
        self.backButton.clicked.connect(self.goBack)

        self.clearButton = QPushButton('Clear', self)
        self.clearButton.setStyleSheet("font-size: 16px; padding: 8px;")
        self.clearButton.setFixedSize(150, 40)
        self.clearButton.clicked.connect(self.clear)

        self.sourceLanguage = QComboBox(self)
        self.sourceLanguage.setFixedSize(150, 40)
        self.sourceLanguage.setStyleSheet("font-size: 14px;")
        self.sourceLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.targetLanguage = QComboBox(self)
        self.targetLanguage.setFixedSize(150, 40)
        self.targetLanguage.setStyleSheet("font-size: 14px;")
        self.targetLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.translateButton = QPushButton('Translate', self)
        self.translateButton.setStyleSheet("font-size: 16px; padding: 8px;")
        self.translateButton.setFixedSize(150, 40)

        self.sourceText = QTextEdit(self)
        self.sourceText.setFont(QFont("Arial", 12))

        self.targetText = QTextEdit(self)
        self.targetText.setFont(QFont("Arial", 12))
        self.targetText.setReadOnly(True)

        topBarLayout = QHBoxLayout()
        topBarLayout.addWidget(self.sourceLanguage, alignment=Qt.AlignLeft)
        topBarLayout.addWidget(self.translateButton, alignment=Qt.AlignCenter)
        topBarLayout.addWidget(self.clearButton, alignment=Qt.AlignCenter)
        topBarLayout.addWidget(self.targetLanguage, alignment=Qt.AlignRight)

        textLayout = QHBoxLayout()
        textLayout.addWidget(self.sourceText)
        textLayout.addWidget(self.targetText)

        mainLayout.addWidget(self.backButton, alignment=Qt.AlignLeft)
        mainLayout.addLayout(topBarLayout)
        mainLayout.addLayout(textLayout)
        self.setLayout(mainLayout)

        self.translateButton.clicked.connect(self.translateButtonClicked)

    def translateButtonClicked(self):
        src_lang_name = self.sourceLanguage.currentText()
        tgt_lang_name = self.targetLanguage.currentText()

        if tgt_lang_name == "Select Language":
            QMessageBox.warning(self, "Error", "Please select a valid target language.")
            return

        tgt_lang = language_code_map.get(tgt_lang_name)

        if not tgt_lang:
            QMessageBox.warning(self, "Error", "Invalid target language selection.")
            return

        source_text = self.sourceText.toPlainText()

        try:
            # First, attempt custom detection
            custom_detected = detect_cebuano_ilocano(source_text)

            if custom_detected:
                detected_lang = custom_detected
            else:
                # Use langdetect as a fallback
                detected_lang = detect(source_text)

            detected_lang_name = next(key for key, value in language_code_map.items() if value == detected_lang)
        except LangDetectException:
            QMessageBox.warning(self, "Error", "Could not detect the source language.")
            return

        # Auto-adjust source language dropdown
        if src_lang_name == "Select Language" or src_lang_name != detected_lang_name:
            src_lang_name = detected_lang_name
            self.sourceLanguage.setCurrentText(src_lang_name)

        src_lang = language_code_map.get(src_lang_name)

        if not src_lang:
            QMessageBox.warning(self, "Error", "Invalid source language detected.")
            return

        translated_text = translate_text(source_text, src_lang, tgt_lang)
        self.targetText.setText(translated_text)

    def clear(self):
        self.sourceText.clear()
        self.targetText.clear()


    def goBack(self):
        self.mainMenuCallback()
        self.close()

class ListeningDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Listening")
        self.setModal(True)
        self.setFixedSize(300, 100)

        self.label = QLabel("Adjusting for ambient noise...", self)
        self.label.setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

    def updateMessage(self, message):
        self.label.setText(message)

    def closeDialog(self):
        self.close()

class SpeechThread(QThread):
    recognized = pyqtSignal(str)
    translated = pyqtSignal(str)
    status_update = pyqtSignal(str)

    def __init__(self, source_lang, target_lang):
        super().__init__()
        self.source_lang = source_lang
        self.target_lang = target_lang

    def run(self):
        self.status_update.emit("Adjusting for ambient noise...")
        self.msleep(2000)  # Simulated delay for noise adjustment
        self.status_update.emit("You can speak now...")

        recognized, translated = recognize_speech(self.source_lang, self.target_lang)

        self.recognized.emit(recognized)
        self.translated.emit(translated)

class VoiceTranslateApp(QWidget):
    def __init__(self, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Voice Translate Interface')
        self.setGeometry(50, 50, 1024, 600)

        mainLayout = QVBoxLayout()

        self.backButton = QPushButton(self)
        self.backButton.setIcon(QIcon('./assets/back.png'))
        self.backButton.setFixedSize(50, 50)
        self.backButton.clicked.connect(self.goBack)

        self.sourceLanguage = QComboBox(self)
        self.sourceLanguage.setFixedSize(150, 40)
        self.sourceLanguage.setStyleSheet("font-size: 14px;")
        self.sourceLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.targetLanguage = QComboBox(self)
        self.targetLanguage.setFixedSize(150, 40)
        self.targetLanguage.setStyleSheet("font-size: 14px;")
        self.targetLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.micButton = QPushButton(self)
        self.micButton.setIcon(QIcon('./assets/mic.png'))
        self.micButton.setFixedSize(50, 50)
        self.micButton.clicked.connect(self.startSpeechRecognition)

        self.micSourceText = QTextEdit(self)
        self.micSourceText.setFont(QFont("Arial", 12))

        self.micTargetText = QTextEdit(self)
        self.micTargetText.setFont(QFont("Arial", 12))
        self.micTargetText.setReadOnly(True)

        topBarLayout = QHBoxLayout()
        topBarLayout.addWidget(self.sourceLanguage, alignment=Qt.AlignLeft)
        topBarLayout.addWidget(self.micButton, alignment=Qt.AlignCenter)
        topBarLayout.addWidget(self.targetLanguage, alignment=Qt.AlignRight)

        micTextLayout = QHBoxLayout()
        micTextLayout.addWidget(self.micSourceText)
        micTextLayout.addWidget(self.micTargetText)

        mainLayout.addWidget(self.backButton, alignment=Qt.AlignLeft)
        mainLayout.addLayout(topBarLayout)
        mainLayout.addLayout(micTextLayout)
        self.setLayout(mainLayout)

    def startSpeechRecognition(self):
        src_lang_name = self.sourceLanguage.currentText()
        tgt_lang_name = self.targetLanguage.currentText()

        if src_lang_name == "Select Language" or tgt_lang_name == "Select Language":
            QMessageBox.warning(self, "Error", "Please select valid languages.")
            return

        src_lang = language_code_map.get(src_lang_name)
        tgt_lang = language_code_map.get(tgt_lang_name)

        if not src_lang or not tgt_lang:
            QMessageBox.warning(self, "Error", "Invalid language selection.")
            return

        self.listeningDialog = ListeningDialog(self)
        self.listeningDialog.show()

        self.speechThread = SpeechThread(src_lang, tgt_lang)
        self.speechThread.status_update.connect(self.listeningDialog.updateMessage)
        self.speechThread.recognized.connect(self.displayRecognizedText)
        self.speechThread.translated.connect(self.displayTranslatedText)
        self.speechThread.finished.connect(self.listeningDialog.closeDialog)
        self.speechThread.start()

    def displayRecognizedText(self, text):
        self.micSourceText.setText(text)

    def displayTranslatedText(self, text):
        self.micTargetText.setText(text)

    def goBack(self):
        self.mainMenuCallback()
        self.close()

class LiveFeedThread(QThread):
    frameCaptured = pyqtSignal(QImage)
    error = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._run_flag = True
        self.initCamera()

    def initCamera(self):
        # Force DirectShow backend
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        if not self.cap.isOpened():
            self.error.emit("Camera initialization failed")
            return False

        # Set properties after successful initialization
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Verify initialization
        ret, _ = self.cap.read()
        if not ret:
            self.cap.release()
            self.error.emit("Camera test frame capture failed")
            return False
            
        return True

    def run(self):
        if not hasattr(self, 'cap') or not self.cap.isOpened():
            self.error.emit("Camera not initialized")
            return

        while self._run_flag:
            ret, frame = self.cap.read()
            if not ret:
                self.error.emit("Frame capture failed")
                break
                
            try:
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                scaled_image = qt_image.scaled(800, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.frameCaptured.emit(scaled_image)
            except Exception as e:
                self.error.emit(f"Image processing error: {str(e)}")
                break

    def stop(self):
        self._run_flag = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
        self.quit()
        self.wait()

class LiveFeedCaptureInterface(QWidget):
    def __init__(self, goToTranslateCallback):
        super().__init__()
        self.goToTranslateCallback = goToTranslateCallback
        self.captured_image_path = None
        self.initUI()
        self.startLiveFeed()

    def initUI(self):
        self.setWindowTitle('Live Camera Feed')
        self.setGeometry(50, 50, 1024, 600)

        self.imageLabel = QLabel(self)
        self.imageLabel.setFixedSize(500, 400)
        self.imageLabel.setStyleSheet("border: 1px solid black;")
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.captureButton = QPushButton("Capture Image", self)
        self.captureButton.setStyleSheet("font-size: 16px; padding: 8px;")
        self.captureButton.setFixedSize(200, 50)
        self.captureButton.clicked.connect(self.captureImage)

        layout = QVBoxLayout()
        layout.addWidget(self.imageLabel, alignment=Qt.AlignCenter)
        layout.addWidget(self.captureButton, alignment=Qt.AlignCenter)
        self.setLayout(layout)

    def startLiveFeed(self):
        self.liveFeedThread = LiveFeedThread()
        self.liveFeedThread.frameCaptured.connect(self.updateLiveFeed)
        self.liveFeedThread.error.connect(self.handleCameraError)
        self.liveFeedThread.start()

    def handleCameraError(self, error_message):
        QMessageBox.critical(self, "Camera Error", error_message)
        self.close()

    def updateLiveFeed(self, image):
        self.imageLabel.setPixmap(QPixmap.fromImage(image))

    def captureImage(self):
        # Capture frame before stopping thread
        ret, frame = self.liveFeedThread.cap.read()
        self.liveFeedThread.stop()

        if ret:
            image_dir = "captured_images"
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.captured_image_path = os.path.join(image_dir, f"{timestamp}.jpg")
            cv2.imwrite(self.captured_image_path, frame)
            self.extractText()
        else:
            QMessageBox.warning(self, "Error", "Failed to capture image")
    
    def extractText(self):
        img = cv2.imread(self.captured_image_path)
        if img is None:
            QMessageBox.warning(self, "Error", "Failed to load captured image")
            return

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Enhance contrast using adaptive thresholding
        enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

        # Perform OCR using EasyOCR
        results = reader.readtext(enhanced)
        extracted_text = " ".join([text for (_, text, _) in results])
        
        # Delete the captured image
        if os.path.exists(self.captured_image_path):
            os.remove(self.captured_image_path)

        if not extracted_text:
            retry = QMessageBox.question(self, "No Text Detected", "No text detected in the image. Would you like to capture another image?", QMessageBox.Yes | QMessageBox.No)
            if retry == QMessageBox.Yes:
                self.startLiveFeed()
            else:
                self.close()
            return

        self.goToTranslateCallback(extracted_text)
        self.close()

class ImageTranslateApp(QWidget):
    def __init__(self, text, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.text_to_translate = text
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Translate Interface')
        self.setGeometry(50, 50, 1024, 600)

        mainLayout = QVBoxLayout()

        self.backButton = QPushButton(self)
        self.backButton.setIcon(QIcon('./assets/back.png'))
        self.backButton.setFixedSize(50, 50)
        self.backButton.clicked.connect(self.goBack)

        self.sourceLanguage = QComboBox(self)
        self.sourceLanguage.setFixedSize(150, 40)
        self.sourceLanguage.setStyleSheet("font-size: 14px;")
        self.sourceLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.targetLanguage = QComboBox(self)
        self.targetLanguage.setFixedSize(150, 40)
        self.targetLanguage.setStyleSheet("font-size: 14px;")
        self.targetLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.translateButton = QPushButton('Translate', self)
        self.translateButton.setStyleSheet("font-size: 16px; padding: 8px;")
        self.translateButton.setFixedSize(150, 40)

        self.sourceText = QTextEdit(self)
        self.sourceText.setFont(QFont("Arial", 12))
        self.sourceText.setText(self.text_to_translate)

        self.targetText = QTextEdit(self)
        self.targetText.setFont(QFont("Arial", 12))
        self.targetText.setReadOnly(True)

        topBarLayout = QHBoxLayout()
        topBarLayout.addWidget(self.sourceLanguage, alignment=Qt.AlignLeft)
        topBarLayout.addWidget(self.translateButton, alignment=Qt.AlignCenter)
        topBarLayout.addWidget(self.targetLanguage, alignment=Qt.AlignRight)

        textLayout = QHBoxLayout()
        textLayout.addWidget(self.sourceText)
        textLayout.addWidget(self.targetText)

        mainLayout.addWidget(self.backButton, alignment=Qt.AlignLeft)
        mainLayout.addLayout(topBarLayout)
        mainLayout.addLayout(textLayout)
        self.setLayout(mainLayout)

        self.translateButton.clicked.connect(self.translateButtonClicked)

    def translateButtonClicked(self):
        src_lang_name = self.sourceLanguage.currentText()
        tgt_lang_name = self.targetLanguage.currentText()

        if src_lang_name == "Select Language" or tgt_lang_name == "Select Language":
            QMessageBox.warning(self, "Error", "Please select valid languages.")
            return

        src_lang = language_code_map.get(src_lang_name)
        tgt_lang = language_code_map.get(tgt_lang_name)

        if not src_lang or not tgt_lang:
            QMessageBox.warning(self, "Error", "Invalid language selection.")
            return

        source_text = self.sourceText.toPlainText()
        translated_text = translate_text(source_text, src_lang, tgt_lang)
        self.targetText.setText(translated_text)

    def clear(self):
        self.sourceText.clear()
        self.targetText.clear()


    def goBack(self):
        self.mainMenuCallback()
        self.close()

class MainMenuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle('Main Menu Interface')
        self.setGeometry(50, 50, 1024, 600)
        
        mainLayout = QVBoxLayout()
        mainLayout.setSpacing(10)
        mainLayout.setAlignment(Qt.AlignCenter) 
        mainLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.textButton = QPushButton('Text Translate', self)
        self.textButton.setFixedSize(600, 60)
        self.textButton.setStyleSheet("background-color: #d1f5d3; font-size: 18px; padding: 10px;")
        self.textButton.clicked.connect(self.openTextTranslate)
        
        self.voiceButton = QPushButton('Voice Translate', self)
        self.voiceButton.setFixedSize(600, 60)
        self.voiceButton.setStyleSheet("background-color: #b0b3ff; font-size: 18px; padding: 10px;")
        self.voiceButton.clicked.connect(self.openVoiceTranslate)
        
        self.imageButton = QPushButton('Image Translate', self)
        self.imageButton.setFixedSize(600, 60)
        self.imageButton.setStyleSheet("background-color: #fcc0c5; font-size: 18px; padding: 10px;")
        self.imageButton.clicked.connect(self.openImageTranslate)
        
        mainLayout.addWidget(self.textButton, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.voiceButton, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.imageButton, alignment=Qt.AlignCenter)

        mainLayout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        self.setLayout(mainLayout)
    
    def openTextTranslate(self):
        self.textTranslateApp = TextTranslateApp(self.showMainMenu)
        self.textTranslateApp.show()
        self.close()
    
    def openVoiceTranslate(self):
        self.voiceTranslateApp = VoiceTranslateApp(self.showMainMenu)
        self.voiceTranslateApp.show()
        self.close()
    
    def openImageTranslate(self):
        self.LiveFeedApp = LiveFeedCaptureInterface(self.goToTranslateCallback)
        self.LiveFeedApp.show()
        self.close()
    
    def showMainMenu(self):
        self.show()

    def goToTranslateCallback(self, text):
        self.imageTranslateApp = ImageTranslateApp(text, self.showMainMenu)
        self.imageTranslateApp.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainMenuApp()
    ex.show()
    sys.exit(app.exec_())