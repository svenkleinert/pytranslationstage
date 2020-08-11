import serial
import serial.tools.list_ports
import time
DEBUG = True

class SMC100PP( ):
    def scan():
        return [d.device for d in serial.tools.list_ports.comports()]

    def from_device( device ):
        return SMC100PP( serial_port=device )

    baudrate = 57600
    controller_states = {
        "0A":"NOT REFERENCED from reset",
        "0B":"NOT REFERENCED from HOMING",
        "0C":"NOT REFERENCED from CONFIGURATION",
        "0D":"NOT REFERENCED from DISABLE",
        "0E":"NOT REFERENCED from READY",
        "0F":"NOT REFERENCED from MOVING",
        "10":"NOT REFERENCED ESP stage error",
        "11":"NOT REFERENCED from JOGGING",
        "14":"CONFIGURATION",
        "1E":"HOMING commanded from RS-232-C",
        "1F":"HOMING commanded by SMC-RC",
        "28":"MOVING",
        "32":"READY from HOMING",
        "33":"READY from MOVING",
        "34":"READY from DISABLE",
        "35":"READY from JOGGING",
        "3C":"DISABLE from READY",
        "3D":"DISABLE from MOVING",
        "3E":"DISABLE from JOGGING",
        "46":"JOGGING from READY",
        "47":"JOGGING from DISABLE"
        }
    def __init__( self, serial_port=None, controller_number=1 ):
        self.retry = 0
        if serial_port is None:
            serial_port = self.serial_port_dialog()

        self.device = serial.Serial( serial_port, self.baudrate, xonxoff=True, timeout=1 )
        if not self.device.is_open:
            self.device.close()
        self.controller_number = str(controller_number)
        if not "READY" in controller_states[self.get_controller_state()]:
            self.reset_controller()
            self.home_search()
        self.name = "SMC100PP (" + serial_port + ")"

        
    def open( self ):
        self.device.open()

    def close( self ):
        self.device.close()

    def write( self, msg ):
        nbytes = self.device.write( (self.controller_number+msg+"\r\n").encode( "utf-8" ) )
        if nbytes == len( msg )+len(self.controller_number)+2:
            return True
        return False

    def read( self ):
        return self.device.read()

    def read_line( self ):
        s = ""
        c = self.device.readline()
        if self.retry < 10:
            try:
                s = c.decode("utf-8").strip()
                self.retry = 0
                return s

            except:
                self.retry +=1
                return self.read_line()
        return ""

    def query( self, msg ):
        if self.write( msg ):
            return self.read_line()
        return ""

    def serial_port_dialog( self ):
        s = ""
        port_list = serial.tools.list_ports.comports()
        for i, port_info in enumerate( port_list ):
            print( port_info.name )
            s+= "\t" + str(i) + ") " + port_info.description + "\n"
        selection = input( "[SMC100PP] Choose serial port:\n" + s )
        return port_list[int(selection)].device

    def reset_controller( self, timeout=30 ):
        if DEBUG:
            print( "[SMC100PP] reset" )
        self.write( "RS" )
        time.sleep(1)
        start = time.time()
        while( self.get_controller_state() != "0A" ):
            if (time.time()-start) > timeout:
                return False
        if self.get_controller_state() == "0A":
            if DEBUG:
                print( "[SMC100PP] reset done!" )
            return True

    def get_controller_state( self ):
        reply = self.query( "TS" )
        state = reply[-2:]
        return state

    def home_search( self, timeout=30 ):
        if DEBUG:
            print( "[SMC100PP] home search" )

        self.write( "OR" )
        start = time.time()
        while self.get_controller_state() == '0A':
            if (time.time()-start) > timeout:
                return False
        while self.get_controller_state() == "1E":
            if (time.time()-start) > timeout:
                return False
        while self.get_controller_state() != "32":
            if (time.time()-start) > timeout:
                return False
        if self.get_controller_state() == "32":
            if DEBUG:
                print( "[SMC100PP] home search done!" )
            return True
        print( self.get_controller_state() )

    def get_position( self ):
        _pos = self.query( "TP" )
        return _pos[3:]

    def move_absolute( self, position, timeout=None ):
        if DEBUG:
            print( "[SMC100PP] move absolute {0:.2f}".format( position ) )
        old_pos = self.query( "PA?" )
        while( "PA" not in old_pos ):
            old_pos = self.query( "PA?" )
        old_pos = old_pos[old_pos.find( "PA" )+2:]
        target = "{0:.2f}".format( position )
        if old_pos == target:
            if DEBUG:
                print( "[SMC100PP] move absolute: no movement required!" )
            return True
        if DEBUG:
                print( "[SMC100PP] move absolute: serial write!" )
        if timeout is None:
            distance = position - float( old_pos )
            timeout = 3 * float( self.query( "PT{0:.2f}".format(distance) )[len(str(self.controller_number))+2:] )
        start = time.time()
        self.write( "PA" + target )
        try:
            _pos = float(self.query( "PA?" )[len(str(self.controller_number))+2:])
        except:
            _pos = 1e30
        while abs( _pos  - float(target) ) < abs( float(old_pos) - float(target) ):
            if (time.time() - start) > timeout:
                return False
            self.write( "PA"+target )
            try:
                _pos = float(self.query( "PA?" )[len(str(self.controller_number))+2:])
            except:
                _pos = 1e30
        if DEBUG:
                print( "[SMC100PP] move absolute: moving!" )
        while self.get_controller_state() != "33":
            if (time.time()-start) > timeout:
                return False
        if self.get_controller_state() == "33":
            if DEBUG:
                print( "[SMC100PP] move absolute done!" )
            return True
        return False

    def move_relative( self, position, timeout=None ):
        while self.get_controller_state() != "28":
            self.write( "PR{0:.2f}".format( position ) )
        if timeout is None:
            timeout = 3 * float( self.query( "PT{0:.2f}".format(position) )[len(str(self.controller_number))+2:] )
        start = time.time()
        while self.get_controller_state() != "33":
            if (time.time() - start ) > timeout:
                return False
        if self.get_controller_state() != "33":
            return True
        return False
