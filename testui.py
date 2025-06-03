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
import platform
import subprocess
from picamera2 import Picamera2
import RPi.GPIO as GPIO

# Add after imports but before other code
class LoadingScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setStyleSheet("background-color: black;")
        self.showFullScreen()
        
        layout = QVBoxLayout()
        
        # Loading image
        image_label = QLabel(self)
        pixmap = QPixmap('./assets/logo.png')  # Your logo/loading image
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        
        # Loading text
        loading_label = QLabel("Loading Assets...", self)
        loading_label.setStyleSheet("color: white; font-size: 24px;")
        loading_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(image_label)
        layout.addWidget(loading_label)
        self.setLayout(layout)
        
        # Start timer to close loading screen
        QTimer.singleShot(3000, self.close)  # 3 seconds

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
cebuano_words = {
    "maayong", "daghang", "salamat", "tabangan", "wala", "kabalo", "asa", "pasidaan!", "pasidaan",
    "buntag", "hapon", "gabii", "palihug", "ayo", "dili", "oo", "diri", "didto",
    "balay", "pagkaon", "tubig", "init", "bugnaw", "kusog", "hinay", "tawo",
    "sakit", "tambalan", "duol", "layo", "kalayo", "peligro", "dalan", "lakaw"
}

ilocano_words = {
    "naimbag", "bigat", "malem", "rabii", "agyamanak", "wen", 
    "saan", "maysa", "dua", "tallo", "uppat", "lima", "innem", "pito",
    "kasta", "kastoy", "dayta", "daytoy", "isu", "adda", "awan", "napintas",
    "balay", "tawen", "init", "lammin", "tao", "nasakit", "ospital", "agbasa"
}

english_words = {
    "hello", "hi", "stop", "warning", "danger", "exit", "enter", "welcome",
    "please", "thank", "thanks", "yes", "no", "help", "open", "close", "ten", "purple", "airfield", "unloading",
    "always", "keep", "right", "left", "maintain", "social", "distancing", "distance", "and", "the",
    "emergency", "caution", "notice", "attention", "warning", "follow", "rules", "safety", "first",
    "use", "wear", "mask", "required", "only", "area", "zone", "authorized", "personnel",
    "do", "not", "push", "pull", "slide", "walk", "run", "way", "this", "that", "direction",
    "in", "out", "up", "down", "stairs", "elevator", "room", "office", "hall", "lobby",
    "information", "counter", "service", "public", "private", "restricted", "wet", "floor", "ceiling"
}

tagalog_words = {
    "salamat", "oo", "hindi", "bakit", "kumusta", "ingat", "baka",
    "pinto", "labas", "loob", "tao", "babala", "tulong", "buksan", "isara",
    "mainit", "malamig", "mabilis", "mabagal", "bahay", "tubig", "pagkain",
    "sakit", "ospital", "delikado", "bawal", "daan", "tama", "mali", "halika",
    "dito", "diyan", "roon", "araw", "gabi", "umaga", "tanghali", "hapon", "gabi"
}

# GPIO Button Configuration
CAPTURE_BTN = 17  # Physical pin 11
LIVEFEED_BTN = 27  # Physical pin 13
MIC_BTN = 22  # Physical pin 15
SCREEN_BTN = 23  # Physical pin 16

def setup_gpio():
    """Initialize GPIO pins with pull-up resistors"""
    try:
        GPIO.setwarnings(False)  # Disable warnings
        GPIO.cleanup()  # Clean up first
        GPIO.setmode(GPIO.BCM)  # Set mode before any operations
        for pin in [CAPTURE_BTN, LIVEFEED_BTN, MIC_BTN, SCREEN_BTN]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    except Exception as e:
        print(f"GPIO Setup Error: {str(e)}")

def cleanup_gpio():
    """Clean up GPIO on program exit"""
    try:
        if GPIO.getmode() is not None:  # Only cleanup if GPIO is initialized
            GPIO.cleanup()
    except Exception as e:
        print(f"GPIO Cleanup Error: {str(e)}")

def detect_language(text):
    """Enhanced language detection for all supported languages."""
    words = set(text.lower().split())
    
    # Count matches for each language
    english_matches = len(words & english_words)
    tagalog_matches = len(words & tagalog_words)
    cebuano_matches = len(words & cebuano_words)
    ilocano_matches = len(words & ilocano_words)
    
    # If any matches found, return the language with most matches
    matches = {
        "en": english_matches,
        "tl": tagalog_matches,
        "ceb": cebuano_matches,
        "ilo": ilocano_matches
    }
    
    max_matches = max(matches.values())
    if max_matches > 0:
        return max(matches.items(), key=lambda x: x[1])[0]
    
    # If no matches, try langdetect with error handling
    try:
        detected = detect(text)
        return detected if detected in ["en", "tl", "ceb", "ilo"] else "en"
    except LangDetectException:
        # Default to English for common signs and instructions
        return "en"

class TextTranslateApp(QWidget):
    def __init__(self, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.virtual_keyboard = None
        self.initUI()
        self.showMaximized()  # Changed from showFullScreen
        self.setWindowFlag(Qt.FramelessWindowHint)

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
        self.sourceLanguage.setEditable(True)
        self.sourceLanguage.setInsertPolicy(QComboBox.NoInsert)  # Prevent user from adding new items

        self.targetLanguage = QComboBox(self)
        self.targetLanguage.setFixedSize(150, 40)
        self.targetLanguage.setStyleSheet("font-size: 14px;")
        self.targetLanguage.addItems(["Select Language", "English", "Tagalog", "Cebuano", "Ilocano"])

        self.translateButton = QPushButton('Translate', self)
        self.translateButton.setStyleSheet("font-size: 16px; padding: 8px;")
        self.translateButton.setFixedSize(150, 40)

        self.sourceText = QTextEdit(self)
        self.sourceText.setFont(QFont("Arial", 12))
        self.sourceText.focusInEvent = lambda e: self.show_keyboard()
        self.sourceText.focusOutEvent = lambda e: self.hide_keyboard()

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.goBack()
        super().keyPressEvent(event)

    def translateButtonClicked(self):
        src_lang_name = self.sourceLanguage.currentText().split(" - ")[0]  # Remove "- Detected" if present
        tgt_lang_name = self.targetLanguage.currentText()

        if tgt_lang_name == "Select Language":
            QMessageBox.warning(self, "Error", "Please select a valid target language.")
            return

        tgt_lang = language_code_map.get(tgt_lang_name)
        if not tgt_lang:
            QMessageBox.warning(self, "Error", "Invalid target language selection.")
            return

        source_text = self.sourceText.toPlainText().strip()
        if not source_text:
            QMessageBox.warning(self, "Error", "Please enter text to translate.")
            return

        # Use enhanced language detection
        detected_lang = detect_language(source_text)
        if not detected_lang:
            QMessageBox.warning(self, "Error", "Could not detect the source language.")
            return

        try:
            detected_lang_name = next(key for key, value in language_code_map.items() if value == detected_lang)
            if src_lang_name == "Select Language":
                # Only show detection if no language was manually selected
                detected_text = f"{detected_lang_name} - Detected"
                self.sourceLanguage.setCurrentText(detected_text)  # Show detected text without adding to items
                src_lang_name = detected_lang_name  # Use the base language name for translation
            src_lang = detected_lang  # Use detected language code directly
        except StopIteration:
            QMessageBox.warning(self, "Error", "Detected language is not supported.")
            return

        translated_text = translate_text(source_text, src_lang, tgt_lang)
        self.targetText.setText(translated_text)

    def show_keyboard(self):
        """Show virtual keyboard"""
        try:
            if not self.virtual_keyboard or self.virtual_keyboard.poll() is not None:
                try:
                    # First try matchbox-keyboard
                    self.virtual_keyboard = subprocess.Popen(['matchbox-keyboard'])
                except FileNotFoundError:
                    try:
                        # Try onboard as fallback
                        self.virtual_keyboard = subprocess.Popen(['onboard'])
                    except FileNotFoundError:
                        print("No virtual keyboard found. Please install matchbox-keyboard or onboard")
        except Exception as e:
            print(f"Keyboard error: {str(e)}")

    def hide_keyboard(self):
        """Hide virtual keyboard"""
        try:
            if self.virtual_keyboard:
                self.virtual_keyboard.terminate()
                self.virtual_keyboard = None
        except Exception as e:
            print(f"Keyboard close error: {str(e)}")

    def clear(self):
        self.sourceText.clear()
        self.targetText.clear()

    def goBack(self):
        self.mainMenuCallback()
        self.close()

    def closeEvent(self, event):
        self.hide_keyboard()
        super().closeEvent(event)

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
        self.showMaximized()  # Changed from showFullScreen
        self.setWindowFlag(Qt.FramelessWindowHint)

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.goBack()
        super().keyPressEvent(event)

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
        self.is_rpi = platform.system() == 'Linux' and platform.machine().startswith('arm')
        self.initCamera()

    def initCamera(self):
        try:
            if self.is_rpi:
                self.cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FPS, 30)
            else:
                self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                self.cap.set(cv2.CAP_PROP_FPS, 30)

            if not self.cap.isOpened():
                self.error.emit("Camera initialization failed")
                return False

            ret, _ = self.cap.read()
            if not ret:
                self.cap.release()
                self.error.emit("Camera test frame capture failed")
                return False

            return True
        except Exception as e:
            self.error.emit(f"Camera initialization error: {str(e)}")
            return False


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

class ExtractionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Processing")
        self.setModal(True)
        self.setFixedSize(300, 100)

        label = QLabel("Extracting text from image...", self)
        label.setAlignment(Qt.AlignCenter)
        layout = QVBoxLayout(self)
        layout.addWidget(label)

class LiveFeedCaptureInterface(QWidget):
    def __init__(self, goToTranslateCallback):
        super().__init__()
        self.goToTranslateCallback = goToTranslateCallback
        self.captured_image_path = None
        self.picam2 = None
        self.timer = QTimer(self)  # Create timer in main thread
        self.timer.timeout.connect(self.update_frame)
        self.setup_capture_button()
        self.initUI()
        # Initialize camera in main thread
        QTimer.singleShot(0, self.initCamera)

    def setup_capture_button(self):
        """Set up GPIO capture button handler"""
        try:
            if GPIO.getmode() is None:
                setup_gpio()
            GPIO.add_event_detect(CAPTURE_BTN, GPIO.FALLING,
                callback=lambda x: QTimer.singleShot(0, self.captureImage),
                bouncetime=300)
        except Exception as e:
            print(f"Capture Button Error: {str(e)}")

    def initUI(self):
        self.setWindowTitle('Live Camera Feed')
        mainLayout = QVBoxLayout()

        # Add back button
        self.backButton = QPushButton(self)
        self.backButton.setIcon(QIcon('./assets/back.png'))
        self.backButton.setFixedSize(50, 50)
        self.backButton.clicked.connect(self.goBack)

        self.imageLabel = QLabel(self)
        self.imageLabel.setFixedSize(640, 480)
        self.imageLabel.setStyleSheet("border: 1px solid black;")
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.captureButton = QPushButton("Capture Image", self)
        self.captureButton.setStyleSheet("font-size: 16px; padding: 8px;")
        self.captureButton.setFixedSize(200, 50)
        self.captureButton.clicked.connect(self.captureImage)

        mainLayout.addWidget(self.backButton, alignment=Qt.AlignLeft)
        mainLayout.addWidget(self.imageLabel, alignment=Qt.AlignCenter)
        mainLayout.addWidget(self.captureButton, alignment=Qt.AlignCenter)
        self.setLayout(mainLayout)
        
        # Set maximize window
        self.showMaximized()  # Changed from showFullScreen
        self.setWindowFlag(Qt.FramelessWindowHint)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.goBack()
        super().keyPressEvent(event)

    def initCamera(self):
        """Initialize camera in main thread"""
        if platform.system() == 'Linux' and platform.machine() in ['armv7l', 'aarch64']:
            self.startPicameraFeed()
        else:
            QMessageBox.critical(self, "Platform Error", "This live feed setup only supports Raspberry Pi.")
            return

    def startPicameraFeed(self):
        try:
            if self.picam2 is None:
                self.picam2 = Picamera2()
                preview_config = self.picam2.create_preview_configuration(
                    main={"size": (640, 480), "format": "RGB888"},
                    buffer_count=4
                )
                self.picam2.configure(preview_config)
            
            self.picam2.start()
            time.sleep(1)  # Brief stabilization
            self.timer.start(33)  # Start timer in main thread
            
        except Exception as e:
            print(f"Camera init error: {str(e)}")

    def update_frame(self):
        try:
            frame = self.picam2.capture_array("main")
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, _ = frame.shape
            image = QImage(frame.data, w, h, 3 * w, QImage.Format_RGB888)
            self.imageLabel.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print(f"Frame update failed: {e}")

    def captureImage(self):
        try:
            if self.timer:
                self.timer.stop()
            
            time.sleep(1)  # Longer stabilization time
            
            # Capture at lower resolution for reliability
            capture_config = self.picam2.create_still_configuration(
                main={"size": (2304, 1296), "format": "RGB888"},
                buffer_count=1
            )
            
            image_dir = "captured_images"
            if not os.path.exists(image_dir):
                os.makedirs(image_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.captured_image_path = os.path.join(image_dir, f"{timestamp}.jpg")
            
            if self.picam2:
                try:
                    # Capture with timeout
                    self.picam2.switch_mode_and_capture_file(
                        capture_config, 
                        self.captured_image_path,
                        timeout=3000  # 3 second timeout
                    )
                    self.extractText()
                except Exception as e:
                    print(f"Capture error: {str(e)}")
                    # Fallback to preview capture
                    array = self.picam2.capture_array()
                    cv2.imwrite(self.captured_image_path, array)
                    self.extractText()
            else:
                QMessageBox.critical(self, "Error", "Camera not initialized")
                return

        except Exception as e:
            QMessageBox.critical(self, "Capture Error", f"Failed to capture image: {str(e)}")
            self.startPicameraFeed()

    def restartCameraFeed(self):
        """Restart camera feed safely"""
        try:
            if self.timer and self.timer.isActive():
                self.timer.stop()
            
            if self.picam2:
                self.picam2.start()
                self.timer.start(33)
        except Exception as e:
            print(f"Failed to restart camera: {str(e)}")

    def extractText(self):
        extraction_dialog = ExtractionDialog(self)
        extraction_dialog.show()
        QApplication.processEvents()

        try:
            img = cv2.imread(self.captured_image_path)
            if img is None:
                extraction_dialog.close()
                QMessageBox.warning(self, "Error", "Failed to load captured image")
                self.restartCameraFeed()  # Restart camera feed
                return

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            enhanced = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

            results = reader.readtext(enhanced)
            extracted_text = " ".join([text for (_, text, _) in results])

            if os.path.exists(self.captured_image_path):
                os.remove(self.captured_image_path)

            extraction_dialog.close()

            if not extracted_text:
                retry = QMessageBox.question(self, "No Text Detected", 
                    "No text detected in the image. Would you like to capture another image?", 
                    QMessageBox.Yes | QMessageBox.No)
                if retry == QMessageBox.Yes:
                    self.restartCameraFeed()  # Changed from startPicameraFeed
                else:
                    self.goBack()  # Changed from self.close()
                return

            self.goToTextTranslateApp(extracted_text)
            self.close()
            
        except Exception as e:
            extraction_dialog.close()
            QMessageBox.critical(self, "Error", f"Failed to extract text: {str(e)}")
            self.restartCameraFeed()  # Restart camera feed after error
            return

    def goToTextTranslateApp(self, text):
        self.textTranslateApp = TextTranslateApp(self.goBackToMainMenu)
        self.textTranslateApp.sourceText.setText(text)
        # Add delay before triggering translation
        QTimer.singleShot(500, self.textTranslateApp.translateButtonClicked)
        self.textTranslateApp.show()
        self.close()

    def goBack(self):
        self.goToTranslateCallback()
        self.close()

    def goBackToMainMenu(self):
        self.goToTranslateCallback()

    def cleanup(self):
        try:
            if self.timer and self.timer.isActive():
                self.timer.stop()
            if self.picam2:
                self.picam2.close()
            if GPIO.getmode() is not None:  # Only remove event if GPIO is initialized
                GPIO.remove_event_detect(CAPTURE_BTN)
        except Exception as e:
            print(f"Cleanup error: {str(e)}")

    def closeEvent(self, event):
        self.cleanup()
        super().closeEvent(event)

class ImageTranslateApp(QWidget):
    def __init__(self, text, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.text_to_translate = text
        self.initUI()
        self.showMaximized()  # Changed from showFullScreen
        self.setWindowFlag(Qt.FramelessWindowHint)

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
        self.sourceLanguage.setEditable(True)
        self.sourceLanguage.setInsertPolicy(QComboBox.NoInsert)  # Prevent user from adding new items

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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.goBack()
        super().keyPressEvent(event)

    def translateButtonClicked(self):
        src_lang_name = self.sourceLanguage.currentText().split(" - ")[0]  # Remove "- Detected" if present
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
        # Show loading screen first
        self.loading = LoadingScreen()
        self.loading.show()
        QApplication.processEvents()
        
        # Initialize main app after loading
        setup_gpio()
        self.setup_gpio_handlers()
        self.initUI()
        self.showMaximized()
        
        # Connect loading screen close to main window show
        self.loading.finished = self.show

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
        super().keyPressEvent(event)

    def setup_gpio_handlers(self):
        """Set up GPIO button event handlers"""
        try:
            # Button 2 (LIVEFEED_BTN): Start speech recognition
            GPIO.add_event_detect(LIVEFEED_BTN, GPIO.FALLING,
                callback=lambda x: QTimer.singleShot(0, self.triggerSpeechRecognition),
                bouncetime=300)
                
            # Button 3 (MIC_BTN): Trigger text translation
            GPIO.add_event_detect(MIC_BTN, GPIO.FALLING,
                callback=lambda x: QTimer.singleShot(0, self.triggerTextTranslation),
                bouncetime=300)

            # Button 4: Handle shutdown directly
            GPIO.add_event_detect(SCREEN_BTN, GPIO.FALLING,
                callback=lambda x: QTimer.singleShot(0, self.handleShutdown),
                bouncetime=300)
        except Exception as e:
            print(f"GPIO Handler Error: {str(e)}")

    def handleShutdown(self):
        """Handle shutdown button press"""
        try:
            reply = QMessageBox.question(self, 'System Shutdown', 
                'Are you sure you want to shutdown?',
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                # Show shutdown message
                msg = QMessageBox()
                msg.setText("Press shutdown button again to confirm")
                msg.setWindowFlags(Qt.FramelessWindowHint)
                msg.show()
                QApplication.processEvents()
                
                # Wait for confirmation
                start_time = time.time()
                while time.time() - start_time < 5:  # 5 second timeout
                    if GPIO.input(SCREEN_BTN) == GPIO.LOW:
                        cleanup_gpio()
                        os.system('sudo shutdown -h now')
                        break
                    time.sleep(0.1)
                msg.close()
        except Exception as e:
            print(f"Shutdown error: {str(e)}")

    def triggerSpeechRecognition(self):
        """Trigger voice recognition from GPIO"""
        # First ensure voice translate interface is open
        if not hasattr(self, 'voiceTranslateApp'):
            self.openVoiceTranslate()
        
        # Wait briefly for UI to initialize
        QApplication.processEvents()
        
        # Now trigger speech recognition
        self.voiceTranslateApp.startSpeechRecognition()

    def triggerTextTranslation(self):
        """Trigger text translation from GPIO"""
        if hasattr(self, 'textTranslateApp') and self.textTranslateApp.isVisible():
            self.textTranslateApp.translateButtonClicked()
        elif hasattr(self, 'imageTranslateApp') and self.imageTranslateApp.isVisible():
            self.imageTranslateApp.translateButtonClicked()

    def toggleScreen(self):
        """Toggle between maximized and fullscreen"""
        if self.isFullScreen():
            self.showMaximized()
        else:
            self.showFullScreen()

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
    
    def showMainMenu(self):
        # Ensure maximize window when returning to main menu
        self.showMaximized()  # Changed from showFullScreen
        self.show()

    def openTextTranslate(self):
        self.textTranslateApp = TextTranslateApp(self.showMainMenu)
        self.textTranslateApp.show()
        self.hide()  # Hide instead of close to maintain window state
    
    def openVoiceTranslate(self):
        self.voiceTranslateApp = VoiceTranslateApp(self.showMainMenu)
        self.voiceTranslateApp.show()
        self.hide()  # Hide instead of close
    
    def openImageTranslate(self):
        self.LiveFeedApp = LiveFeedCaptureInterface(self.goToTranslateCallback)
        self.LiveFeedApp.show()
        self.hide()  # Hide instead of close
    
    def goToTranslateCallback(self, text=None):  # Make text parameter optional
        if text:
            self.imageTranslateApp = ImageTranslateApp(text, self.showMainMenu)
            self.imageTranslateApp.show()
        else:
            # Just show main menu if no text provided
            self.show()

    def closeEvent(self, event):
        cleanup_gpio()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    try:
        ex = MainMenuApp()
        ex.show()
        app.exec_()
    finally:
        cleanup_gpio()