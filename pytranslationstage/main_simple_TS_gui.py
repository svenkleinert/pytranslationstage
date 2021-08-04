import sys

def main():
    from pytranslationstage.gui import QApplication, AbstractTranslationStageWidget
    app = QApplication( sys.argv )
    dialog = AbstractTranslationStageWidget()
    dialog.show()
    sys.exit( app.exec_() )

if __name__ == "__main__":
    main()
