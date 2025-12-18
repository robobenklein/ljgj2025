
import arcade
import lark
from .assets import assets_dir
from .parser import (
    parse, tree_to_ast, _Instruction,
)


class ChalkActor(arcade.Sprite):
    """
    An actor can execute instructions and interact with other objects or actors in the level.
    """
    def __init__(self):
        super().__init__(
            assets_dir / "char1.png",
            scale=1/4,
        )

    def setup(self, tobj, level):
        self.level = level
        self.ast = None
        self.cur_instruction = None
        self.instructions = None

        self.name = tobj.name

        # determine position based on the object bounds:
        assert len(tobj.shape) == 2, f"actor map object shape should be 2D spawn point"
        print(f"actor {self.name} at {tobj.shape}")
        self.position = tobj.shape

    def load_code_block(self, block):
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
        if not self.instructions:
            # actor has nothing to do!
            # needs some better indicator of "Idleness"
            # for now let's just spin lol
            self.turn_right(10)
            return
        # runs the current instruction
        if self.cur_instruction >= len(self.instructions):
            print("reached end of actor instructions!")
            self.cur_instruction = 0
            return
        i = self.instructions[self.cur_instruction]
        if not isinstance(i, _Instruction):
            print(f"Can't execute this: {i}")
            self.cur_instruction += 1
            return

        # make functions in this class the same as the intruction class name
        getattr(self, i.__class__.__name__)(i)

    def InsMove(self, params):
        # TODO: Error handling if the id does not exist
        moveToObj = self.level.interactables[
            f"{params.location_type} {params.location_identifier}"
        ];

        # Get the obj's position, then adjust it by the side we access it from and the actor's height/width
        # TODO: This assumes Desk right now, add handling for the other destinations
        match moveToObj.access_side:
                case "top":
                    endPoint = (moveToObj.position.x, moveToObj.bounds.top + self.height / 2)
                case "bottom":
                    endPoint = (moveToObj.position.x, moveToObj.bounds.bottom - self.height / 2)
                case "left":
                    endPoint = (moveToObj.bounds.left - self.width / 2, moveToObj.position.y)
                case "right":
                    endPoint = (moveToObj.bounds.right + self.width / 2, moveToObj.position.y)

        # TODO: Pathfind instead of teleportation
        self.position = endPoint

        # if we have reached the destination of the move command:
        # step the instruction pointer forward
        self.cur_instruction += 1

class Desk(arcade.Sprite):
    def __init__(self):
        super().__init__(
            assets_dir / "chalk-desk1.png",
            scale=1/4,
        )

    def setup(self, tobj):
        # original data from loading the Tiled object
        self._tobj = tobj

        self.name = tobj.name.lower()
        print(f"desk name {self.name}")

        # determine position based on the object bounds:
        self.bounds = arcade.LRBT(
            min(x[0] for x in tobj.shape),
            max(x[0] for x in tobj.shape),
            min(x[1] for x in tobj.shape),
            max(x[1] for x in tobj.shape),
        )
        print(f"desk bounds {self.bounds}")
        self.position = self.bounds.center

        self.access_side = tobj.properties["access_side"];
        print(f"desk access-side {self.access_side}")


    def tick(self):
        # TODO: what does a desk need to update each game tick?
        # probably something related to game logic (win state checks and inbox/outboxing?)
        pass
