import pyvisa
import pyvisa.constants
import time
from .AbstractStage import AbstractStage
DEBUG = True

class SMC100PP(AbstractStage):
    @classmethod
    def scan(cls):
        rm = pyvisa.ResourceManager()
        return [r[1].alias for r in rm.list_resources_info("ASRL?*::INSTR").items()]

    @classmethod
    def from_device(cls, device):
        return cls(serial_port=device)

    translation_limits = (-0.04, 0.04)
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
        self.device.timeout = 3

        self.controller_number = str(controller_number)
        if not "READY" in self.controller_states[self.get_controller_state()]:
            self.reset_controller()
            self.home_search()
        self.name = __name__ + " (" + serial_port + ")"


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
        s = ""
        while self.device.bytes_in_buffer > 0:
            s += self.device.read()
        return s

    def query( self, msg, delay=0.5, timeout=None ):
        try:
            if timeout is not None:
                timeout *= 1000
                tmp_timeout = self.device.timeout
                self.device.timeout = timeout
            res = self.device.query( self.controller_number + msg, delay )

            if timeout is not None:
                self.device.timeout = tmp_timeout
            return res
        except Exception:
            s = ""
            while self.device.bytes_in_buffer > 0:
                s += self.device.read()
            if timeout is not None:
                self.device.timeout = tmp_timeout
            return s

    def serial_port_dialog( self ):
        s = ""
        port_list = [r[1].alias for r in self.resource_manager.list_resources_info("ASRL?*::INSTR").items()]
        for i, port_info in enumerate( port_list ):
            s+= "\t" + str(i) + ") " + port_info + "\n"
        selection = input( "[SMC100PP] Choose serial port:\n" + s )
        return port_list[int(selection)]

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
            print( "[SMC100PP] move absolute {0:.3f}".format( position ) )
        old_pos = self.query( "PA?" )
        while( "PA" not in old_pos ):
            old_pos = self.query( "PA?" )
            if DEBUG:
                print( "[SMC100PP] move absolute: get_position" )
        old_pos_str = old_pos[old_pos.find( "PA" )+2:]
        old_pos = float( old_pos_str )
        if abs(old_pos - position*1000)<0.02:
            if DEBUG:
                print( "[SMC100PP] move absolute: no movement required!" )
            return True
        if DEBUG:
                print( "[SMC100PP] move absolute: serial write!" )

        if timeout is None:
            distance = abs(position * 1000 - old_pos)
            timeout = self.query( "PT{0:.2f}".format(distance) )
            try:
                timeout = 1.5 * float( timeout[timeout.find("PT")+2:] )
            except:
                timeout = 15
            timeout = min( timeout, 15 )
        target = "{0:.4f}".format(position * 1000)
        start = time.time()
        now = start
        pos = old_pos
        while (now - start) < timeout:
            self.write("PA" + target)
            pos_str = self.query( "PA?" )
            pos_str = pos_str[pos_str.find("PA")+2:]
            try:
                pos = float( pos_str ) * 1e-3
            except:
                pass
            if ( abs(pos - position)<2e-7 ):
                break
            time.sleep(0.1)
            now = time.time()

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
            self.write( "PR{0:.2f}".format( position * 1000 ) )
        if timeout is None:
            timeout = 3 * float( self.query( "PT{0:.2f}".format(position) )[len(str(self.controller_number))+2:] )
        start = time.time()
        while self.get_controller_state() != "33":
            if (time.time() - start ) > timeout:
                return False
        if self.get_controller_state() != "33":
            return True
        return False
