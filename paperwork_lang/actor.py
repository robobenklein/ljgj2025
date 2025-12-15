
import arcade
import lark
from .assets import assets_dir
from .parser import parse_text


class ChalkActor(arcade.Sprite):
    """
    An actor can execute instructions and interact with other objects or actors in the level.
    """
    def setup(self, level):
        self.level = level

    def run_code_block(self, block):
        try:
            ast = parse_text(block)
        except lark.exceptions.UnexpectedInput:
            # TODO somehow we gotta return feedback to the user
            print(f"bad code yo")

        print(f"running da code yo")
        print(ast.pretty())

    def perform_instruction(self, instruction):
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