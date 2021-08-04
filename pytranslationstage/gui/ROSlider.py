from . import QSlider, Slot, Qt

import types

class ROSlider( QSlider ):
    def __init__( self ):
        super( ROSlider, self ).__init__( )

    def setReadOnly( self, read_only ):
        if read_only:
            self.mousePressEvent = self.dummy_function
            self.keyPressEvent = self.dummy_function
        else:
            self.mousePressEvent = super( ROSlider, self ).mousePressEvent
            self.keyPressEvent = super( ROSlider, self ).keyPressEvent

    @Slot()
    def dummy_function( self, *args ):
        pass
