
import arcade

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor, Desk
from ..level import ChalkLevel

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
    """
    level_filename = 'menu1.json'

    def setup(self):
        super().setup()
        self.player = self.actors[0]

    def execution_step(self):
        super().execution_step()
