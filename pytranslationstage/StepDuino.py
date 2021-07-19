import pyvisa
from .AbstractStage import AbstractStage

class StepDuino(AbstractStage):
    @classmethod
    def scan():
        rm = pyvisa.ResourceManager()
        return [r[1].alias for r in rm.list_resources_info("ASRL?*::INSTR").items()]

    @classmethod
    def from_device(cls, device):
        return cls(serial_port=device)

    def __init__(self, serial_port=None, baudrate=115200, resource_manager=None):
        if resource_manager is None:
            resource_manager = pyvisa.ResourceManager()
        
        if serial_port is None:
            serial_port = self.serial_port_dialog()
        self.device = self.resource_manager.open_resource(serial_port)

        self.device.baud_rate=baudrate
        self.device.timeout = 3
    
        self.name = __name__ + " (" + serial_port + ")"

        if self._controller_state != "RE":
            self._home_search()

        self.position = self.get_position()

    def _write(self, msg):
        nbytes = self.device.write(msg)
        if nbytes == len(msg):
            return True
        return False

    def _query(self, msg):
        return self.device.query(msg)

    def _home_search(self, timeout=30):
        self._write("HO")
        while self._controller_state(self) == "MO":
            pass

        if self._controller_state(self) == "RE":
            return True

        return False

    def _controller_state(self):
        return self._query("ST?")

    
    def move_absolute(self, position):
        self._write("MA{0:.5f}".format(position))
        while self._controller_state(self) == "MO":
            pass
        if self.get_position() != position:
            return False
        return True

    def move_relative(self, position):
        self._write("MR{0:.5f}".format(position))
        while self._controller_state(self) == "MO":
            pass
        old_pos = self.position
        if self.get_position() - old_pos != position:
            return False
        return True

    def get_position(self):
        pos = self._query("GA?")
        try:
            self.position = float(pos)
        except Exception as e:
            print( pos, e )
            self.position = None
    
        return self.position
