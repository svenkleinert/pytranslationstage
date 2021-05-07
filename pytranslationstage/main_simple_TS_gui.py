import sys

def main():
    from  gui import USE_PYQT5, USE_PYSIDE2
    if USE_PYSIDE2:
        from PySide2.QtWidgets import QApplication
    elif USE_PYQT5:
        from PyQt5.QtWidgets import QApplication
    from gui import AbstractTranslationStageWidget
    app = QApplication( sys.argv )
    dialog = AbstractTranslationStageWidget()
    dialog.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
