import serial
import serial.tools.list_ports
import time
from .AbstractStage import AbstractStage


class StepDuino(serial.Serial, AbstractStage):
    @classmethod
    def scan(cls):
        res = []
        for port in serial.tools.list_ports.comports():
            res.append(port.device)
        return res


    @classmethod
    def from_device(cls, device):
        return cls(serial_port=device)

    def __init__(self, serial_port=None, baudrate=115200, timeout=None):
        if serial_port is None:
            serial_port = self.serial_port_dialog()
        super(StepDuino, self).__init__(serial_port, baudrate=baudrate, timeout=timeout)
        self.id = serial_port
        self.name = __name__ + " (" + serial_port + ")"
        
        if timeout is None:
            self.timeout = 1

        if not self.is_open:
            self.open()
        
        time.sleep(1.5) # wait until arduino boot finished

        self._get_translation_limits()

        if self._controller_state != "READY":
            self._home_search()

        self.position = self.get_position()

    def _write(self, msg):
        if self.out_waiting != 0:
            self.reset_output_buffer()
        nbytes = self.write((msg + '\n').encode("utf-8"))
        if nbytes == len(msg)+1:
            return True
        return False

    @classmethod
    def _validate_answer(cls, msg, response):
        if msg == response[:len(msg)]:
            return response[len(msg):]
        else:
            return ""

    def _query(self, msg, delay=None, validate=True):
        if self.in_waiting != 0:
            self.reset_input_buffer()
        if self._write(msg):
            if delay is not None:
                time.sleep(delay)
            try:
                response = self.read_until().decode("utf-8")[:-2]
                if ' ' in msg:
                    msg = msg.split(' ')[0]
                if validate:
                    return self._validate_answer(msg, response)
                return response
            except UnicodeDecodeError as e:
                print( "Warning:", e )
                self.reset_input_buffer()
                return ""
        else:
            return ""


    def _get_translation_limits(self):
        response = self._query("MOVE:LIMITS:MAXIMUM?")
        try:
            _max = float(response)
        except Exception as e:
            _max = None

        response = self._query("MOVE:LIMITS:MINIMUM?")
        try:
            _min = float(response)
        except Exception as e:
            _min = None

        self.translation_limits = (_min, _max)
        return self.translation_limits



    def _home_search(self, timeout=30):
        tmp_timeout = self.timeout
        self.timeout = timeout * 1000
        self._write("SYSTEM:HOME")
        while self._controller_state() == "MOVING":
            pass
        
        self.timeout = tmp_timeout
        if self._controller_state() == "READY":
            return True

        return False

    def _controller_state(self):
        response = self._query("SYSTEM:STATE?")
        if response != "":
            return response
        return "COMMERROR"

    
    def move_absolute(self, position):
        try:
            time_for_move = float(self._query("MOVE:ABSOLUTE? {0:.6f}".format(position)))
        except Exception as e:
            print("WARNING:", e)
            time_for_move = 1
        self._write("MOVE:ABSOLUTE {0:.6f}".format(position))
        time.sleep(float(time_for_move))
        while self._controller_state() == "MOVING":
            time.sleep(0.3)
        if self.get_position() != position:
            return False
        return True

    def move_relative(self, position):
        try:
            time_for_move = float(self._query("MOVE:RELATIVE? {0:.6f}".format(position)))
        except Exception as e:
            print("WARNING:", e)
            time_for_move = 1

        self._write("MOVE:RELATIVE {0:.6f}".format(position))
        time.sleep(float(time_for_move))
        while self._controller_state() == "MOVING":
            time.sleep(0.3)
        old_pos = self.position
        if self.get_position() - old_pos != position:
            return False
        return True

    def get_position(self):
        response = self._query("MOVE:POSITION?")
        try:
            self.position = float(response)
        except Exception as e:
            self.position = None
        return self.position

