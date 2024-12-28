from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QComboBox, QTextEdit, QVBoxLayout, QHBoxLayout, QMessageBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys

class TextTranslateApp(QWidget):
    def __init__(self, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Text Translate Interface')
        self.setGeometry(100, 100, 800, 600)

        # Layout
        mainLayout = QVBoxLayout()

        self.translateButton = QPushButton('Translate', self)
        self.translateButton.setStyleSheet("font-size: 14px; padding: 5px;")

        self.backButton = QPushButton(self)
        self.backButton.setIcon(QIcon('back_icon.png'))  # Replace with a valid back icon
        self.backButton.setFixedSize(40, 40)
        self.backButton.clicked.connect(self.goBack)
        
        sourceLanguage = QComboBox(self)
        sourceLanguage.addItems(["Select Language", "English", "Spanish", "French", "German"])

        targetLanguage = QComboBox(self)
        targetLanguage.addItems(["Select Language", "English", "Spanish", "French", "German"])

        self.sourceText = QTextEdit(self)
        self.targetText = QTextEdit(self)
        self.targetText.setReadOnly(True)

        topBarLayout = QHBoxLayout()
        topBarLayout.addWidget(sourceLanguage)
        topBarLayout.addWidget(self.translateButton)
        topBarLayout.addWidget(targetLanguage)

        textLayout = QHBoxLayout()
        textLayout.addWidget(self.sourceText)
        textLayout.addWidget(self.targetText)

        mainLayout.addWidget(self.backButton, alignment=Qt.AlignLeft)
        mainLayout.addLayout(topBarLayout)
        mainLayout.addLayout(textLayout)
        self.setLayout(mainLayout)

    def goBack(self):
        self.mainMenuCallback()
        self.close()

class VoiceTranslateApp(QWidget):
    def __init__(self, mainMenuCallback):
        super().__init__()
        self.mainMenuCallback = mainMenuCallback
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Voice Translate Interface')
        self.setGeometry(100, 100, 800, 600)

        # Layout
        mainLayout = QVBoxLayout()

        self.micButton = QPushButton(self)
        self.micButton.setIcon(QIcon('mic_icon.png'))  # Replace with a valid microphone icon
        self.micButton.setFixedSize(40, 40)
        self.micButton.clicked.connect(self.showMicPopup)

        self.translateButton = QPushButton('Translate', self)
        self.translateButton.setStyleSheet("font-size: 14px; padding: 5px;")

        sourceLanguage = QComboBox(self)
        sourceLanguage.addItems(["Select Language", "English", "Spanish", "French", "German"])

        targetLanguage = QComboBox(self)
        targetLanguage.addItems(["Select Language", "English", "Spanish", "French", "German"])

        self.micSourceText = QTextEdit(self)
        self.micTargetText = QTextEdit(self)
        self.micTargetText.setReadOnly(True)

        topBarLayout = QHBoxLayout()
        topBarLayout.addWidget(sourceLanguage)
        topBarLayout.addWidget(self.micButton)
        topBarLayout.addWidget(self.translateButton)
        topBarLayout.addWidget(targetLanguage)

        micTextLayout = QHBoxLayout()
        micTextLayout.addWidget(self.micSourceText)
        micTextLayout.addWidget(self.micTargetText)

        self.backButton = QPushButton(self)
        self.backButton.setIcon(QIcon('back_icon.png'))  # Replace with a valid back icon
        self.backButton.setFixedSize(40, 40)
        self.backButton.clicked.connect(self.goBack)

        mainLayout.addWidget(self.backButton, alignment=Qt.AlignLeft)
        mainLayout.addLayout(topBarLayout)
        mainLayout.addLayout(micTextLayout)
        self.setLayout(mainLayout)

    def showMicPopup(self):
        QMessageBox.information(self, "Microphone", "Microphone is now recording.")

    def goBack(self):
        self.mainMenuCallback()
        self.close()

class MainMenuApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Menu Interface')
        self.setGeometry(100, 100, 800, 600)

        # Layout
        mainLayout = QVBoxLayout()

        self.textButton = QPushButton('Text Translate', self)
        self.textButton.setStyleSheet("background-color: #d1f5d3; font-size: 18px; padding: 10px;")
        self.textButton.clicked.connect(self.openTextTranslate)

        self.voiceButton = QPushButton('Voice Translate', self)
        self.voiceButton.setStyleSheet("background-color: #b0b3ff; font-size: 18px; padding: 10px;")
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
