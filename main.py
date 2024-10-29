import sys
from PyQt5.QtWidgets import QApplication
from text_editor import TextEditor

if __name__ == "__main__":
    app = QApplication(sys.argv)
    editor = TextEditor()

    # Check if a file path was passed as a command-line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        editor.openFile(file_path)

    editor.show()
    sys.exit(app.exec_())
