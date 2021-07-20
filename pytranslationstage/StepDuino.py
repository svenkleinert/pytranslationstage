import pyvisa
from .AbstractStage import AbstractStage

class StepDuino(AbstractStage):
    @classmethod
    def scan(cls):
        rm = pyvisa.ResourceManager()
        res = []
        for r in rm.list_resources_info("ASRL?*::INSTR").items():
            if r[1].alias is None:
                res.append(r[0])
            else:
                res.append(r[1].alias)
        return res


    @classmethod
    def from_device(cls, device):
        return cls(serial_port=device)

    def __init__(self, serial_port=None, baudrate=9600, resource_manager=None):
        if resource_manager is None:
            resource_manager = pyvisa.ResourceManager()
        
        if serial_port is None:
            serial_port = self.serial_port_dialog()
        self.device = resource_manager.open_resource(serial_port)

        self.device.baud_rate=baudrate
        self.device.data_bits = 8
        self.device.parity = pyvisa.constants.Parity.none
        self.device.stop_bits = pyvisa.constants.StopBits.one
        self.device.write_termination = "\r\n"
        self.device.read_termination = ""

        self.device.timeout = 1000
    
        self.name = __name__ + " (" + serial_port + ")"
        self.device.open()
        self.device.write("*IDN?")
        print( self.device.read())
        print( self._query("*IDN?") )
        if self._controller_state != "READY":
            self._home_search()

        self.position = self.get_position()

    def _write(self, msg):
        nbytes = self.device.write(msg)
        print(nbytes, len(msg))
        if nbytes == len(msg):
            return True
        return False

    def _query(self, msg):
        return self.device.query(msg)

    def _home_search(self, timeout=30):
        tmp_timeout = self.device.timeout
        self.device.timeout = timeout * 1000
        self._write("SYSTEM:HOME")
        while self._controller_state() == "MOVING":
            pass
        
        self.device.timeout = tmp_timeout
        if self._controller_state() == "REEADY":
            return True

        return False

    def _controller_state(self):
        return self._query("SYSTEM:STATE?")

    
    def move_absolute(self, position):
        self._write("MOVE:ABSOLUTE{0:.6f}".format(position))
        while self._controller_state() == "MOVING":
            pass
        if self.get_position() != position:
            return False
        return True

    def move_relative(self, position):
        self._write("MOVE:RELATIVE{0:.6f}".format(position))
        while self._controller_state() == "MOVING":
            pass
        old_pos = self.position
        if self.get_position() - old_pos != position:
            return False
        return True

    def get_position(self):
        pos = self._query("MOVE:POSITION?")
        try:
            self.position = float(pos)
        except Exception as e:
            print( pos, e )
            self.position = None
    
        return self.position
