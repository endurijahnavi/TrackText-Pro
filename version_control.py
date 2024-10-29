import os
import json
from datetime import datetime
from PyQt5.QtWidgets import QMessageBox

def loadVersionHistory(filePath):
    versionDir = getVersionDirectory(filePath)
    if not versionDir:
        return []
    historyFileName = os.path.join(versionDir, "history.json")
    if not os.path.exists(historyFileName):
        return []

    try:
        with open(historyFileName, 'r', encoding='utf-8') as historyFile:
            return json.load(historyFile)
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to load version history:\n{str(e)}")
        return []

def saveVersion(content, message, filePath):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    versionDir = getVersionDirectory(filePath)
    if not versionDir:
        QMessageBox.warning(None, "Error", "No file selected for version control.")
        return
    os.makedirs(versionDir, exist_ok=True)
    versionFileName = os.path.join(versionDir, f"{timestamp}.txt")

    try:
        with open(versionFileName, 'w', encoding='utf-8') as versionFile:
            versionFile.write(content)
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to save version:\n{str(e)}")
        return

    versionInfo = {"timestamp": timestamp, "message": message}
    updateVersionHistory(versionDir, versionInfo)

def getReadableTimestamp(timestamp):
    try:
        readable_time = datetime.strptime(timestamp, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        return readable_time
    except:
        return timestamp

def getVersionDirectory(filePath):
    if not filePath:
        return None
    baseName = os.path.basename(filePath)
    versionDir = os.path.join(os.path.expanduser("~/.version_control_text_editor"), baseName)
    return versionDir

def updateVersionHistory(versionDir, versionInfo):
    historyFileName = os.path.join(versionDir, "history.json")
    try:
        if os.path.exists(historyFileName):
            with open(historyFileName, 'r', encoding='utf-8') as historyFile:
                history = json.load(historyFile)
        else:
            history = []

        history.append(versionInfo)

        with open(historyFileName, 'w', encoding='utf-8') as historyFile:
            json.dump(history, historyFile, indent=4)
    except Exception as e:
        QMessageBox.warning(None, "Error", f"Failed to update version history:\n{str(e)}")
