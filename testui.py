from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox, QDialog)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys
from backend import translate_text, recognize_speech

# Language code mapping
language_code_map = {
    "English": "en",
    "Tagalog": "tl",
    "Cebuano": "ceb",
    "Ilocano": "ilo"
}

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
        self.clearButton.setStyleSheet("font-size: 14px; padding: 5px;")
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
        topBarLayout.addWidget(self.clearButton)
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

class MainMenuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Menu Interface')
        self.setGeometry(50, 50, 1024, 600)

        mainLayout = QVBoxLayout()

        self.textButton = QPushButton('Text Translate', self)
        self.textButton.setStyleSheet("background-color: #d1f5d3; font-size: 20px; padding: 12px;")
        self.textButton.setFixedSize(600, 60)
        self.textButton.clicked.connect(self.openTextTranslate)

        self.voiceButton = QPushButton('Voice Translate', self)
        self.voiceButton.setStyleSheet("background-color: #b0b3ff; font-size: 20px; padding: 12px;")
        self.voiceButton.setFixedSize(600, 60)
        self.voiceButton.clicked.connect(self.openVoiceTranslate)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(self.textButton)
        buttonLayout.addWidget(self.voiceButton)
        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)

    def openTextTranslate(self):
        self.textTranslateApp = TextTranslateApp(self.showMainMenu)
        self.textTranslateApp.show()
        self.close()

    def openVoiceTranslate(self):
        self.voiceTranslateApp = VoiceTranslateApp(self.showMainMenu)
        self.voiceTranslateApp.show()
        self.close()

    def showMainMenu(self):
        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainMenuApp()
    ex.show()
    sys.exit(app.exec_())
