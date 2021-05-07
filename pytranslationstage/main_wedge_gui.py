
import sys

def main():
    from  pytranslationstage.gui import USE_PYQT5, USE_PYSIDE2
    if USE_PYSIDE2:
        from PySide2.QtWidgets import QApplication
    elif USE_PYQT5:
        from PyQt5.QtWidgets import QApplication
    from pytranslationstage.gui import WedgeScanningWidget
    app = QApplication( sys.argv )
    dialog = WedgeScanningWidget( show_scan_button=True )
    dialog.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
