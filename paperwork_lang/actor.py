
import arcade
import lark
from .assets import assets_dir
from .parser import parse, tree_to_ast


class ChalkActor(arcade.Sprite):
    """
    An actor can execute instructions and interact with other objects or actors in the level.
    """
    def setup(self, level):
        self.level = level
        self.ast = None
        self.cur_instruction = None
        self.instructions = None

    def run_code_block(self, block):
        """
        Loads the program into the actor and enables execution
        """
        try:
            self.ptree = parse(block)
        except lark.exceptions.UnexpectedInput as e:
            # TODO somehow we gotta return feedback to the user
            print(f"bad code yo")
            print(e)
            # print stacktrace
            import traceback
            traceback.print_exc()
            return

        self.ast = tree_to_ast(self.ptree)
        print(f"running da code yo")
        self.cur_instruction = 0
        self.instructions = self.ast.lines
        for i in self.instructions:
            print(i)

    def tick(self):
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

    def tick(self):
        # TODO: what does a desk need to update each game tick?
        # probably something related to game logic (win state checks and inbox/outboxing?)
        pass
