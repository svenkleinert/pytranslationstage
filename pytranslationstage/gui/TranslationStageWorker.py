from . import QThread, Signal

class TranslationStageWorker( QThread ):
    updateSignal = Signal( int )

    def __init__( self, function, argument=None ):
        super( TranslationStageWorker, self ).__init__()
        self.function = function
        self.argument = argument
        self.return_value = None

    def run( self ):
        if self.argument is None:
            self.return_value = self.function()
            self.updateSignal.emit( 0 )
        if isinstance( self.argument, str ) or (not hasattr( self.argument, "__iter__" )):
            self.return_value = self.function( self.argument )
            self.updateSignal.emit( 0 )
        else:
            self.return_value = []
            for i, arg in enumerate( self.argument ):
                self.return_value.append( self.function( arg ) )
                self.updateSignal.emit( i )
