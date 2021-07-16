from .. import USE_PYQT5, USE_PYSIDE2
if USE_PYSIDE2:
    from PySide2.QtWidgets import QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QRadioButton, QMessageBox, QLineEdit, QSlider, QFormLayout
    from PySide2.QtCore import Slot, Signal, Qt, QThread
elif USE_PYQT5:
    from PyQt5.QtWidgets import QWidget, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGroupBox, QRadioButton, QMessageBox, QLineEdit, QSlider, QFormLayout
    from PyQt5.QtCore import pyqtSlot as Slot, pyqtSignal as Signal, Qt, QThread

from .AbstractTranslationStageWidget import AbstractTranslationStageWidget
from .WedgeScanningWidget import WedgeScanningWidget
