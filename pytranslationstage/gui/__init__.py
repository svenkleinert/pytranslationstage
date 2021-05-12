if not "USE_PYSIDE2" in globals():
    global USE_PYSIDE2
    USE_PYSIDE2 = True

if not "USE_PYQT5" in globals():
    global USE_PYQT5
    USE_PYQT5 = not USE_PYSIDE2

from .AbstractTranslationStageWidget import AbstractTranslationStageWidget
from .WedgeScanningWidget import WedgeScanningWidget
