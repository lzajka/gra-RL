from enum import Enum
from functools import cached_property

class Action(Enum):
    MOVE_LEFT       = 0
    MOVE_RIGHT      = 1
    SHOOT           = 2

    def to_vector(self):
        z = self._zero_vector
        z[self.value] = 1
        return z

    @cached_property
    def action_count(self):
        return 3
        
    @cached_property
    def _zero_vector(self):
        arr = [0] * self.action_count
        return arr