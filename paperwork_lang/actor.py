
import arcade
from .assets import assets_dir

class ChalkActor(arcade.Sprite):
    def setup(self):
        pass

    def instruction(self, instruction):
        pass

class Desk(arcade.Sprite):
    def __init__(self):
        super().__init__(
            assets_dir / "chalk-desk1.png",
            scale=1/4,
        )

    def setup(self, tobj):
        # original data from loading the Tiled object
        self._tobj = tobj

        # determine position based on the object bounds:
        self.bounds = arcade.LRBT(
            min(x[0] for x in tobj.shape),
            max(x[0] for x in tobj.shape),
            min(x[1] for x in tobj.shape),
            max(x[1] for x in tobj.shape),
        )
        print(f"desk bounds {self.bounds}")
        self.position = self.bounds.center