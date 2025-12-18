
import arcade

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor, Desk
from ..level import ChalkLevel
from .level1 import Level1

class PlayerActor(ChalkActor):
    def __init__(self):
        super().__init__(
            assets_dir / "char1.png",
            # assets_dir / "chalk-desk1.png",
            scale=1/4,
        )

class MenuLevel(ChalkLevel):
    """
    The menu level is a special case where the player can issue commands directly to the Actor in real time to move around.

    I don't think any other level is going to do something like this.
    
    Current flow: Move to Desk C, Take from Desk C, Move to Desk A/B, Drop to select level A/B 
    """
    level_filename = 'menu1.json'

    def setup(self, owner):
        super().setup(owner)
        self.player = self.actors[0]

        self.interactables["desk b"].interact = self.load_level_1

    def execution_step(self):
        super().execution_step()

    def load_level_1(self):
        self.owner.add_level(Level1)
