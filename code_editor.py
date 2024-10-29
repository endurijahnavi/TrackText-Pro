import os
import json
import difflib
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt, QRect  # <-- Import QRect here
from PyQt5.QtGui import QColor, QPainter, QTextCharFormat, QTextCursor, QFont
from line_number_area import LineNumberArea

class CodeEditor(QPlainTextEdit):
    textChangedSignal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.lineNumberArea = LineNumberArea(self)
        self.blockCountChanged.connect(self.updateLineNumberAreaWidth)
        self.updateRequest.connect(self.updateLineNumberArea)
        self.cursorPositionChanged.connect(self.highlightCurrentLine)
        self.textChanged.connect(self.emitTextChanged)
        self.updateLineNumberAreaWidth(0)

        # Setting the font and style
        self.setFont(QFont("Consolas", 10))
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #dfffff;
                selection-background-color: #264f78;
                border: 1px solid #000000;
                caret-color: #ffffff;
            }
        """)

    def lineNumberAreaWidth(self):
        return 50  # Fixed width in pixels

    def updateLineNumberAreaWidth(self, _):
        self.setViewportMargins(self.lineNumberAreaWidth(), 0, 0, 0)

    def updateLineNumberArea(self, rect, dy):
        if dy:
            self.lineNumberArea.scroll(0, dy)
        else:
            self.lineNumberArea.update(0, rect.y(), self.lineNumberArea.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.updateLineNumberAreaWidth(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.lineNumberArea.setGeometry(QRect(cr.left(), cr.top(), self.lineNumberAreaWidth(), cr.height()))

    def lineNumberAreaPaintEvent(self, event):
        painter = QPainter(self.lineNumberArea)
        painter.fillRect(event.rect(), QColor(30, 30, 30))

        block = self.firstVisibleBlock()
        blockNumber = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(blockNumber + 1)
                painter.setPen(QColor(128, 128, 128))
                painter.drawText(0, top, self.lineNumberArea.width(), self.fontMetrics().height(),
                                 Qt.AlignCenter, number)

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            blockNumber += 1

    def highlightCurrentLine(self):
        extraSelections = []

        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            lineColor = QColor(20, 20, 20)
            selection.format.setBackground(lineColor)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extraSelections.append(selection)

        self.setExtraSelections(extraSelections)

    def displayDiff(self, diff_lines):
        self.clear()
        cursor = self.textCursor()

        for line in diff_lines:
            if line.startswith('+'):
                cursor.insertText(line + '\n', self.getTextCharFormat(QColor(0, 180, 0)))  # Green for additions
            elif line.startswith('-'):
                cursor.insertText(line + '\n', self.getTextCharFormat(QColor(180, 0, 0)))  # Red for deletions
            else:
                cursor.insertText(line + '\n')

    def getTextCharFormat(self, color):
        text_format = QTextCharFormat()
        text_format.setForeground(color)
        return text_format

    def emitTextChanged(self):
        self.textChangedSignal.emit(self.toPlainText())
