import pyvisa 
import pyvisa.constants
import time
DEBUG = True

class SMC100PP( ):
    def scan():
        rm = pyvisa.ResourceManager()
        return [r[1].alias for r in rm.list_resources_info("ASRL?*::INSTR").items()]

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
    def __init__( self, serial_port=None, resource_manager=None, controller_number=1 ):
        self.retry = 0
        if resource_manager is None:
            resource_manager = pyvisa.ResourceManager()
        self.resource_manager = resource_manager
        
        if serial_port is None:
            serial_port = self.serial_port_dialog()
        self.device = self.resource_manager.open_resource( serial_port )
        self.device.baud_rate = self.baudrate
        self.device.data_bits = 8
        self.device.parity = pyvisa.constants.Parity.none
        self.device.stop_bits = pyvisa.constants.StopBits.one
        self.device.set_visa_attribute(pyvisa.constants.VI_ATTR_ASRL_FLOW_CNTRL, pyvisa.constants.VI_ASRL_FLOW_XON_XOFF)
        self.device.write_termination = "\r\n"
        self.device.read_termination = "\r\n"

        self.controller_number = str(controller_number)
        if not "READY" in self.controller_states[self.get_controller_state()]:
            self.reset_controller()
            self.home_search()
        self.name = "SMC100PP (" + serial_port + ")"

        
    def open( self ):
        self.device.open()

    def close( self ):
        self.device.close()

    def write( self, msg ):
        nbytes = self.device.write( self.controller_number + msg )
        if nbytes == len( msg )+len(self.controller_number)+2:
            return True
        return False

    def read( self ):
        return self.device.read()

    def query( self, msg ):
        try:
            return self.device.query( self.controller_number + msg, 0.5 )
        except Exception as inst:
            print( inst )

    def serial_port_dialog( self ):
        s = ""
        port_list = [r[1].alias for r in self.resource_manager.list_resources_info("ASRL?*::INSTR").items()]
        for i, port_info in enumerate( port_list ):
            print( port_info )
            s+= "\t" + str(i) + ") " + port_info + "\n"
        selection = input( "[SMC100PP] Choose serial port:\n" + s )
        return port_list[int(selection)].device

    def reset_controller( self, timeout=30 ):
        return
        if DEBUG:
            print( "[SMC100PP] reset" )
        self.write( "RS" )
        time.sleep(3)
        start = time.time()
        while( self.get_controller_state() != "0A" ):
            print( "test" )
            if (time.time()-start) > timeout:
                return False
        if self.get_controller_state() == "0A":
            if DEBUG:
                print( "[SMC100PP] reset done!" )
            return True

    def get_controller_state( self ):
        reply = self.query( "TS" )
        try:
            if len( reply ) > 2:
                state = reply[-2:]
                return state
        except TypeError:
            pass
        return "0A"

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
        try:
            old_pos = self.query( "PA?" )
            while( "PA" not in old_pos ):
                old_pos = self.query( "PA?" )
        except TypeError:
            old_pos = "PA010"
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
            timeout = self.query( "PT{0:.2f}".format(distance) )
            try:
                timeout = 2.5 * float( timeout[len(str(self.controller_number))+2:] )
            except TypeError:
                timeout = 15
            timeout = min( timeout, 15 )

        start = time.time()
        self.write( "PA" + target )
        try:
            _pos = float(self.query( "PA?" )[len(str(self.controller_number))+2:])
        except ValueError:
            _pos = 1e30
        except TypeError:
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
