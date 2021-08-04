import sys

def main():
    from pytranslationstage.gui import QApplication, WedgeScanningWidget
    app = QApplication( sys.argv )
    dialog = WedgeScanningWidget( show_scan_button=True )
    dialog.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
