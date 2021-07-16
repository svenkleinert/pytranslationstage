from .SMC100PP import SMC100PP

__version__ = "0.0.2"

DEBUG = False
USE_PYQT5 = True
USE_PYSIDE2 = not USE_PYQT5

translation_stage_types = { "Newport SMC100PP" : SMC100PP }

if DEBUG:
    from .DebugStage import DebugStage
    translation_stage_types.update( {"DebugStage" : DebugStage} )
