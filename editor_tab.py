import os
import json
from datetime import datetime
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QMessageBox
from code_editor import CodeEditor

class EditorTab(QWidget):
    def __init__(self, parent=None, filePath=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.editor = CodeEditor()
        self.layout.addWidget(self.editor)
        self.setLayout(self.layout)
        self.currentFile = filePath
        self.versionHistory = []
        if self.currentFile:
            self.loadVersionHistory()

    def getVersionDirectory(self):
        if not self.currentFile:
            return None
        baseName = os.path.basename(self.currentFile)
        versionDir = os.path.join(os.path.expanduser("~/.version_control_text_editor"), baseName)
        return versionDir

    def loadVersionHistory(self):
        versionDir = self.getVersionDirectory()
        if not versionDir:
            self.versionHistory = []
            return
        historyFileName = os.path.join(versionDir, "history.json")
        if not os.path.exists(historyFileName):
            self.versionHistory = []
            return

        try:
            with open(historyFileName, 'r', encoding='utf-8') as historyFile:
                self.versionHistory = json.load(historyFile)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load version history:\n{str(e)}")
            self.versionHistory = []

    def updateVersionHistory(self, history):
        versionDir = self.getVersionDirectory()
        if not versionDir:
            return
        historyFileName = os.path.join(versionDir, "history.json")
        try:
            with open(historyFileName, 'w', encoding='utf-8') as historyFile:
                json.dump(history, historyFile, indent=4)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update version history:\n{str(e)}")

    def saveVersion(self, content, message):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        versionDir = self.getVersionDirectory()
        if not versionDir:
            QMessageBox.warning(self, "Error", "No file selected for version control.")
            return
        os.makedirs(versionDir, exist_ok=True)
        versionFileName = os.path.join(versionDir, f"{timestamp}.txt")

        try:
            with open(versionFileName, 'w', encoding='utf-8') as versionFile:
                versionFile.write(content)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save version:\n{str(e)}")
            return

        versionInfo = {"timestamp": timestamp, "message": message}
        self.versionHistory.append(versionInfo)
        self.updateVersionHistory(self.versionHistory)

    def getReadableTimestamp(self, timestamp):
        try:
            readable_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
            return readable_time
        except:
            return timestamp
