from PyQt5.QtWidgets import QPlainTextEdit
from PyQt5.QtCore import QProcess, Qt
from PyQt5.QtGui import QTextCursor, QCursor

class TerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #dfffff;
                font-family: Consolas, monospace;
                font-size: 10pt;
            }
        """)
        self.setCursor(QCursor(Qt.IBeamCursor))
        self.setUndoRedoEnabled(False)

        self.process = QProcess(self)
        self.process.setProgram("cmd.exe")
        self.process.setProcessChannelMode(QProcess.MergedChannels)

        # Connect signals
        self.process.readyRead.connect(self.readOutput)
        self.process.started.connect(self.onProcessStarted)
        self.process.finished.connect(self.onProcessFinished)

        # Start cmd.exe
        self.process.start()

    def onProcessStarted(self):
        self.moveCursor(QTextCursor.End)
        self.setFocus()

    def onProcessFinished(self, exitCode, exitStatus):
        self.insertPlainText(f"\nTerminal exited with code {exitCode}.\n")
        self.moveCursor(QTextCursor.End)

    def readOutput(self):
        data = self.process.readAll()
        text = bytes(data).decode('utf-8')
        self.insertPlainText(text)
        self.moveCursor(QTextCursor.End)

    def keyPressEvent(self, event):
        cursor = self.textCursor()
        block = cursor.block()
        blockStart = block.position()
        blockText = block.text()

        if cursor.position() < blockStart + len(blockText):
            self.moveCursor(QTextCursor.End)
            return

        if event.key() == Qt.Key_Backspace:
            if cursor.position() > blockStart:
                super().keyPressEvent(event)
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.executeCommand()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_C:
            self.copy()
        elif event.modifiers() == Qt.ControlModifier and event.key() == Qt.Key_V:
            self.paste()
        else:
            super().keyPressEvent(event)

    def executeCommand(self):
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        text = self.toPlainText()
        last_prompt_index = text.rfind('>')
        if last_prompt_index == -1:
            command = text.strip()
            self.setPlainText('')
        else:
            command = text[last_prompt_index + 1:].strip()
            cursor.setPosition(last_prompt_index + 1)
            cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
        if command:
            self.process.write((command + '\r\n').encode())
        self.moveCursor(QTextCursor.End)

    def contextMenuEvent(self, event):
        menu = self.createStandardContextMenu()
        copyAction = QAction("Copy", self)
        copyAction.setShortcut("Ctrl+C")
        copyAction.triggered.connect(self.copy)
        pasteAction = QAction("Paste", self)
        pasteAction.setShortcut("Ctrl+V")
        pasteAction.triggered.connect(self.paste)
        menu.addAction(copyAction)
        menu.addAction(pasteAction)
        menu.exec_(event.globalPos())
