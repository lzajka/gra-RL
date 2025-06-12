from enum import Enum

class GhostState(Enum):
    """Enum reprezentujący stany ducha w grze Pacman.
    """
    CHASE = "CHASE"
    SCATTER = "SCATTER"
    FRIGHTENED = "FRIGHTENED"
    NOT_SPAWNED = "NOT_SPAWNED"