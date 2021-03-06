VERBOSE = True
import sys
import time
from .AbstractStage import AbstractStage

class DebugStage(AbstractStage):
    name = __name__
    translation_limits = (-0.1, 0.1)
    id = 0

    @classmethod
    def scan(cls):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return ["Debug Stage"]

    @classmethod
    def from_device(cls, device):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return cls()

    def __init__( self, serial_port=None, controller_number=1 ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        self.position = 0


    def open( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        pass

    def close( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        pass

    def write( self, msg ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return True

    def read( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return True

    def read_line( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return True

    def query( self, msg ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        if self.write( msg ):
            return self.read_line()
        return ""

    def reset_controller( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        self.position = 0


    def get_controller_state( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return True

    def home_search( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return True

    def get_position( self ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        return self.position

    def move_absolute( self, position ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        self.position = position
        time.sleep( 0.5 )
        return True

    def move_relative( self, position ):
        if VERBOSE:
            print( "[" + __name__ + "] " + sys._getframe().f_code.co_name )
        self.position += position
        return True
