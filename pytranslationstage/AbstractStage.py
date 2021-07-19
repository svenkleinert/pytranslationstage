from abc import ABC

class AbstractStage(ABC):
    @property
    def translation_limits(self):
        raise NotImplementedError("translation_limits")
    @classmethod
    def scan(cls):
        raise NotImplementedError("scan(cls)")

    @classmethod
    def from_device(cls, device):
        raise NotImplementedError("from_device(cls, device)")

    def get_position(self):
        raise NotImplementedError("get_position()")
    
    def move_absolute(self, position):
        raise NotImplementedError("move_absolute(position)")

    def move_relative(self, position):
        raise NotImplementedError("move_relative(position)")
