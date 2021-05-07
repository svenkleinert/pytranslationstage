from .SMC100PP import SMC100PP

__version__ = "0.0.2"

DEBUG = False

translation_stage_types = { "Newport SMC100PP" : SMC100PP }

if "DEBUG" in globals():
    if DEBUG:
        from .DebugStage import DebugStage
        translation_stage_types.update( {"DebugStage" : DebugStage} )
