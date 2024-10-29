import os
import json
import difflib
from datetime import datetime
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QDockWidget, QListWidget, QVBoxLayout,
    QMessageBox, QInputDialog, QAction, QFileDialog, QToolBar, QPushButton
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt  # <-- Import Qt here
from terminal_widget import TerminalWidget
from editor_tab import EditorTab
from styles import get_menu_style, get_tab_style, get_toolbar_style

class TextEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TrackText - Pro")
        self.resize(1700, 1100)

        self.setupSidePanels()
        self.setupTabWidget()
        self.setupMenu()
        self.setupToolbar()

    def setupTabWidget(self):
        self.tabWidget = QTabWidget()
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabCloseRequested.connect(self.closeTab)
        self.tabWidget.currentChanged.connect(self.onTabChanged)
        self.setCentralWidget(self.tabWidget)

        if self.tabWidget.count() == 0:
            self.addNewTab()

        # Apply styles
        self.tabWidget.setStyleSheet(get_tab_style())

    def addNewTab(self, filePath=None):
        newTab = EditorTab(self, filePath)
        fileName = os.path.basename(filePath) if filePath else "Untitled"
        self.tabWidget.addTab(newTab, fileName)
        self.tabWidget.setCurrentWidget(newTab)

        newTab.editor.textChangedSignal.connect(self.onTextChanged)

    def closeTab(self, index):
        if self.tabWidget.count() == 1:
            QMessageBox.warning(self, "Warning", "Cannot close the last tab.")
            return
        self.tabWidget.removeTab(index)

    def onTabChanged(self, index):
        self.updateVersionHistoryPanel()

    def getCurrentTab(self):
        current_widget = self.tabWidget.currentWidget()
        return current_widget if isinstance(current_widget, EditorTab) else None

    def setupMenu(self):
        menuBar = self.menuBar()
        menuBar.setStyleSheet(get_menu_style())

        # File Menu
        fileMenu = menuBar.addMenu("&File")
        newTabAction = QAction("&New Tab", self)
        newTabAction.setShortcut("Ctrl+N")
        newTabAction.triggered.connect(self.addNewTab)
        fileMenu.addAction(newTabAction)

        openAction = QAction("&Open", self)
        openAction.setShortcut("Ctrl+O")
        openAction.triggered.connect(self.openFile)
        fileMenu.addAction(openAction)

        saveAction = QAction("&Save", self)
        saveAction.setShortcut("Ctrl+S")
        saveAction.triggered.connect(self.saveFile)
        fileMenu.addAction(saveAction)

        saveAsAction = QAction("Save &As", self)
        saveAsAction.triggered.connect(self.saveFileAs)
        fileMenu.addAction(saveAsAction)

        closeTabAction = QAction("&Close Tab", self)
        closeTabAction.setShortcut("Ctrl+W")
        closeTabAction.triggered.connect(lambda: self.closeTab(self.tabWidget.currentIndex()))
        fileMenu.addAction(closeTabAction)

        exitAction = QAction("&Exit", self)
        exitAction.triggered.connect(self.close)
        fileMenu.addAction(exitAction)

        # Version Control Menu
        versionMenu = menuBar.addMenu("&Version Control")
        commitAction = QAction("&Commit Changes", self)
        commitAction.triggered.connect(self.commitChanges)
        versionMenu.addAction(commitAction)

        diffAction = QAction("&Show Diff", self)
        diffAction.triggered.connect(self.showDiff)
        versionMenu.addAction(diffAction)

    def setupSidePanels(self):
        # Version History Dock
        self.versionHistoryDock = QDockWidget("Version History", self)
        self.versionHistoryDock.setFeatures(QDockWidget.NoDockWidgetFeatures)

        self.versionHistoryList = QListWidget(self)
        self.versionHistoryList.setStyleSheet("""
            QListWidget {
                background-color: #2e2e2e;
                color: #ffffff;
                border: none;
            }
            QListWidget::item:selected {
                background-color: #444444;
            }
        """)
        self.versionHistoryList.itemClicked.connect(self.loadSelectedVersion)
        self.versionHistoryDock.setWidget(self.versionHistoryList)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.versionHistoryDock)

        # Terminal Dock
        self.terminalDock = QDockWidget("Terminal", self)
        self.terminalDock.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable)
        self.terminalWidget = TerminalWidget(self)
        self.terminalDock.setWidget(self.terminalWidget)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.terminalDock)

    def setupToolbar(self):
        toolbar = QToolBar("Side Panels")
        toolbar.setMovable(False)
        toolbar.setStyleSheet(get_toolbar_style())

        historyIcon = QIcon.fromTheme("document-open")
        self.versionHistoryButton = QPushButton(historyIcon, "History")
        self.versionHistoryButton.setCheckable(True)
        self.versionHistoryButton.setChecked(True)
        self.versionHistoryButton.clicked.connect(self.toggleVersionHistory)
        toolbar.addWidget(self.versionHistoryButton)

        terminalIcon = QIcon.fromTheme("utilities-terminal")
        self.terminalButton = QPushButton(terminalIcon, "Terminal")
        self.terminalButton.setCheckable(True)
        self.terminalButton.setChecked(True)
        self.terminalButton.clicked.connect(self.toggleTerminal)
        toolbar.addWidget(self.terminalButton)

        self.addToolBar(toolbar)

    def toggleVersionHistory(self):
        self.versionHistoryDock.setVisible(self.versionHistoryButton.isChecked())

    def toggleTerminal(self):
        self.terminalDock.setVisible(self.terminalButton.isChecked())

    def openFile(self, filePath=None, checked=False):
        if not filePath:
            filePath, _ = QFileDialog.getOpenFileName(self, "Open File")

        if filePath:
            # Check if file is already open
            for index in range(self.tabWidget.count()):
                tab = self.tabWidget.widget(index)
                if tab.currentFile == filePath:
                    self.tabWidget.setCurrentIndex(index)
                    return

            self.addNewTab(filePath)

            try:
                with open(filePath, 'r', encoding='utf-8') as file:
                    self.getCurrentTab().editor.setPlainText(file.read())
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to open file:\n{str(e)}")
            self.getCurrentTab().loadVersionHistory()
            self.updateVersionHistoryPanel()

    def saveFile(self):
        currentTab = self.getCurrentTab()
        if not currentTab:
            return

        if not currentTab.currentFile:
            self.saveFileAs()
            return

        try:
            with open(currentTab.currentFile, 'w', encoding='utf-8') as file:
                file.write(currentTab.editor.toPlainText())
            self.updateVersionHistoryPanel()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to save file:\n{str(e)}")

    def saveFileAs(self):
        currentTab = self.getCurrentTab()
        if not currentTab:
            return

        fileName, _ = QFileDialog.getSaveFileName(self, "Save File As")
        if fileName:
            currentTab.currentFile = fileName
            self.tabWidget.setTabText(self.tabWidget.currentIndex(), os.path.basename(fileName))
            self.saveFile()

    def commitChanges(self):
        currentTab = self.getCurrentTab()
        if not currentTab:
            return

        if not currentTab.currentFile:
            QMessageBox.warning(self, "Error", "Please save the file before committing changes.")
            return

        history = currentTab.versionHistory
        commitOptions = ["New Commit"] + [
            f"{currentTab.getReadableTimestamp(entry['timestamp'])}: {entry['message']}" 
            for entry in history
        ]
        selectedOption, ok = QInputDialog.getItem(
            self, 
            "Commit Changes", 
            "Select commit:", 
            commitOptions, 
            0, 
            False
        )

        if not ok:
            return

        message, ok_message = QInputDialog.getText(
            self, 
            "Commit Changes", 
            "Enter commit message:"
        )
        if not ok_message or not message:
            return

        content = currentTab.editor.toPlainText()

        if selectedOption == "New Commit":
            currentTab.saveVersion(content, message)
        else:
            commitIndex = commitOptions.index(selectedOption) - 1
            if commitIndex < 0 or commitIndex >= len(history):
                QMessageBox.warning(self, "Error", "Invalid commit selection.")
                return
            history[commitIndex]['message'] = message
            timestamp = history[commitIndex]['timestamp']
            versionDir = currentTab.getVersionDirectory()
            versionFileName = os.path.join(versionDir, f"{timestamp}.txt")
            try:
                with open(versionFileName, 'w', encoding='utf-8') as versionFile:
                    versionFile.write(content)
                currentTab.updateVersionHistory(history)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to commit changes:\n{str(e)}")
                return

        self.updateVersionHistoryPanel()

    def showDiff(self):
        currentTab = self.getCurrentTab()
        if not currentTab:
            return

        if not currentTab.currentFile:
            QMessageBox.warning(self, "Error", "Please save the file to view diffs.")
            return

        history = currentTab.versionHistory
        historyList = [
            f"{currentTab.getReadableTimestamp(entry['timestamp'])}: {entry['message']}" 
            for entry in history
        ]

        if not historyList:
            QMessageBox.information(self, "Diff Viewer", "No versions available for comparison.")
            return

        selectedItem, ok = QInputDialog.getItem(
            self, 
            "Diff Viewer", 
            "Select a version to compare:", 
            historyList, 
            0, 
            False
        )
        if ok and selectedItem:
            index = historyList.index(selectedItem)
            self.compareWithVersion(currentTab, index)

    def compareWithVersion(self, tab, index):
        if not tab.currentFile:
            return

        history = tab.versionHistory
        timestamp = history[index]['timestamp']
        versionDir = tab.getVersionDirectory()
        versionFileName = os.path.join(versionDir, f"{timestamp}.txt")

        if not os.path.exists(versionFileName):
            QMessageBox.warning(self, "Error", "Failed to load the selected version for comparison.")
            return

        try:
            with open(versionFileName, 'r', encoding='utf-8') as versionFile:
                oldContent = versionFile.read()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to read the selected version:\n{str(e)}")
            return

        currentContent = tab.editor.toPlainText()

        diff = difflib.unified_diff(
            oldContent.splitlines(),
            currentContent.splitlines(),
            fromfile="Previous Version",
            tofile="Current Version",
            lineterm=""
        )

        diffText = list(diff)
        tab.editor.displayDiff(diffText)

    def loadSelectedVersion(self, item):
        currentTab = self.getCurrentTab()
        if not currentTab:
            return

        history = currentTab.versionHistory
        selectedText = item.text()
        try:
            readable_time, message = selectedText.split(": ", 1)
            timestamp = datetime.strptime(readable_time, "%Y-%m-%d %H:%M:%S").strftime("%Y%m%d%H%M%S")
        except:
            QMessageBox.warning(self, "Error", "Invalid version format.")
            return

        versionDir = currentTab.getVersionDirectory()
        versionFileName = os.path.join(versionDir, f"{timestamp}.txt")

        if os.path.exists(versionFileName):
            try:
                with open(versionFileName, 'r', encoding='utf-8') as versionFile:
                    content = versionFile.read()
                    self.resetEditorToDefault(currentTab, content)
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to load the selected version:\n{str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Failed to load the selected version")

    def resetEditorToDefault(self, tab, content):
        tab.editor.clear()
        tab.editor.setPlainText(content)
        cursor = tab.editor.textCursor()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(tab.editor.getDefaultCharFormat())

    def updateVersionHistoryPanel(self):
        try:
            self.versionHistoryList.clear()
        except AttributeError:
            QMessageBox.warning(self, "Error", "Version History panel is not initialized.")
            return

        currentTab = self.getCurrentTab()
        if not currentTab:
            return
        history = currentTab.versionHistory
        for entry in history:
            readable_time = currentTab.getReadableTimestamp(entry['timestamp'])
            self.versionHistoryList.addItem(f"{readable_time}: {entry['message']}")

    def onTextChanged(self):
        # Placeholder for any future text changed handling
        pass
