from .SMC100PP import SMC100PP

DEBUG = True

translation_stage_types = { "Newport SMC100PP" : SMC100PP }

if "DEBUG" in globals():
    if DEBUG:
        from .DebugStage import DebugStage
        translation_stage_types.update( {"DebugStage" : DebugStage} )
