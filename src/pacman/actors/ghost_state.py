from enum import Enum

class GhostState(Enum):    
    """Enum reprezentujący stany ducha w grze Pacman.
    """
    CHASE = "chase"
    SCATTER = "scatter"
    FRIGHTENED = "frightened"
    EATEN = "eaten"