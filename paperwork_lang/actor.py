
import arcade
import lark

from collections import namedtuple
ParcelParams = namedtuple("ParcelParams", ["parcel_type", "parcel_identifier"])

from .assets import assets_dir
from .parser import (
    parse, tree_to_ast, _Instruction, InsDrop
)
from .inventory import ActorInventory
from .itemfactory import ItemFactory


class ChalkActor(arcade.Sprite):
    """
    An actor can execute instructions and interact with other objects or actors in the level.
    """
    def __init__(self):
        super().__init__(
            assets_dir / "char1.png",
            scale=1/4,
        )
        self.saved_code_block = "" # Don't reset the user's code, so don't place in setup

    def setup(self, tobj, level):
        self.level = level
        self.ast = None
        self.cur_instruction = 0
        self.instructions = None
        self.name = tobj.name
        
        # TODO: Allow specifying inventory capacity for docs/box/carts (two arms, two carts? Stack boxes?)
        #   Right now it's unlimited space
        self.inventory = ActorInventory()

        # determine position based on the object bounds:
        assert len(tobj.shape) == 2, f"actor map object shape should be 2D spawn point"
        print(f"actor {self.name} at {tobj.shape}")
        self.position = tobj.shape
        self.angle = 0

    def load_code_block(self, block):
        """
        Loads the program into the actor and enables execution
        """
        try:
            self.ptree = parse(block)
        except lark.exceptions.UnexpectedInput as e:
            # TODO somehow we gotta return feedback to the user
            print(f"bad code yo: {block}")
            print(e)
            # print stacktrace
            import traceback
            traceback.print_exc()
            return

        self.ast = tree_to_ast(self.ptree)
        print(f"running da code yo")
        self.cur_instruction = 0
        self.instructions = self.ast.lines
        self.labels = {}

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
            self.cur_instruction = 0
            return

        instruction = self.instructions[self.cur_instruction]
        print(f"line {self.cur_instruction} code: {instruction}")
        while not isinstance(instruction, _Instruction):
            label = instruction.split('#', 1)[1].lstrip()
            self.labels[label] = self.cur_instruction

            self.cur_instruction += 1
            if self.cur_instruction >= len(self.instructions):
                self.cur_instruction = 0
                return

            instruction = self.instructions[self.cur_instruction]
            print(f"line {self.cur_instruction} code: {instruction}")

        # make functions in this class the same as the intruction class name
        if getattr(self, instruction.__class__.__name__)(instruction):
            # if we have finished the command:
            # step the instruction pointer forward
            self.cur_instruction += 1

    def InsMove(self, params):
        # TODO: Error handling if the id does not exist
        interactableID = f"{params.location_type} {params.location_identifier}"
        if interactableID in self.level.interactables:
            moveToObj = self.level.interactables[interactableID]
        else:
            return True

        # Get the obj's position, then adjust it by the side we access it from and the actor's height/width
        if moveToObj.__class__ == Desk:
            match moveToObj.access_side:
                case "top":
                    endPoint = (moveToObj.position.x, moveToObj.bounds.top + self.height / 2)
                    endDirection_degrees = 0
                case "bottom":
                    endPoint = (moveToObj.position.x, moveToObj.bounds.bottom - self.height / 2)
                    endDirection_degrees = 180
                case "left":
                    endPoint = (moveToObj.bounds.left - self.width / 2, moveToObj.position.y)
                    endDirection_degrees = 270
                case "right":
                    endPoint = (moveToObj.bounds.right + self.width / 2, moveToObj.position.y)
                    endDirection_degrees = 90
        else:
            raise NotImplementedError

        # TODO: Pathfind instead of teleportation
        self.position = endPoint
        self.angle = endDirection_degrees

        return True # Finished, if not true, then we get re-called

    def InsTake(self, params):
        # Find the interactable in 'front' of us, if there exists one (otherwise fail)
        match self.angle:
            case 0: # Facing down
                overlapRect = arcade.XYWH(self.center_x, self.center_y - self.width / 2, self.width, self.height * 2)
            case 90: # Facing left
                overlapRect = arcade.XYWH(self.center_x - self.width / 2, self.center_y, self.width * 2, self.height)
            case 180: # Facing up
                overlapRect = arcade.XYWH(self.center_x, self.center_y + self.width / 2, self.width, self.height * 2)
            case 270: # Facing right
                overlapRect = arcade.XYWH(self.center_x + self.width / 2, self.center_y, self.width * 2, self.height)
            case _: # If we are not axis aligned, then we are not at a desk
                return True

        # TODO: Make the interactables also contain sprite lists to iterate through?
        overlaps = arcade.get_sprites_in_rect(overlapRect, self.level.desks)
        if len(overlaps) == 0:
            print(f"InsTake debug no overlaps")
            return True

        # TODO: Should only be 1 overlap, but could be a bug later
        interactable = overlaps[0]
        if len(overlaps) > 1:
            print(f"InsTake overlapped with {len(overlaps)} objects! Defaulting to the first right now")

        if params.parcel_type == "doc" or params.parcel_type == "any":
            if interactable.__class__ == Desk:
                # If the object can take the document, remove it from our inventory
                ID = interactable.interact(params)
                if ID >= 0:
                    if ID == params.parcel_identifier:
                        print(f"InsTake retrieved doc: {params.parcel_identifier}")
                        self.inventory.add_item(params)
                    else:
                        print(f"InsTake retrieved doc: {ID}")
                        self.inventory.add_item(ParcelParams("doc", ID))

                return True
            elif params.parcel_type != "any": # Can only take docs from desks
                return True
            # Let 'any' try the other options

        # TODO: Handle other types

    def InsDrop(self, params):
        if self.inventory.contains_item(params) == False:
            print(f"InsDrop actor {self.name} does not contain item {params.parcel_type} with ID {params.parcel_identifier}")
            return True

        # TODO: Handle 'ANY' type
        # Docs must be at a desk to drop them (Don't want to scatter paapers all over the floor!)
        if params.parcel_type == "doc":
            # Find the interactable in 'front' of us, if there exists one (otherwise fail)
            match self.angle:
                case 0: # Facing down
                    overlapRect = arcade.XYWH(self.center_x, self.center_y - self.width / 2, self.width, self.height * 2)
                case 90: # Facing left
                    overlapRect = arcade.XYWH(self.center_x - self.width / 2, self.center_y, self.width * 2, self.height)
                case 180: # Facing up
                    overlapRect = arcade.XYWH(self.center_x, self.center_y + self.width / 2, self.width, self.height * 2)
                case 270: # Facing right
                    overlapRect = arcade.XYWH(self.center_x + self.width / 2, self.center_y, self.width * 2, self.height)
                case _: # If we are not axis aligned, then we are not at a desk
                    return True

            overlaps = arcade.get_sprites_in_rect(overlapRect, self.level.desks)
            if len(overlaps) == 0:
                print(f"InsDrop debug no overlaps")
                return True

            # TODO: Should only be 1 overlap, but could be a bug later
            interactable = overlaps[0]
            if len(overlaps) > 1:
                print(f"InsDrop overlapped with {len(overlaps)} objects! Defaulting to the first right now")

            # If the object can take the document, remove it from our inventory
            if params.parcel_identifier != None:
                if interactable.interact(params):
                    self.inventory.remove_item(params)
            else:
                # Specifically need to make a InsDrop so the interactable knows it's getting an item
                newParams = InsDrop(params.parcel_type, self.inventory.get_first_itemID(params.parcel_type))
                if interactable.interact(newParams):
                    self.inventory.remove_item(newParams)

        # TODO: Handle other types

    def InsWhen(self, params):
        def InventoryCheck(params):
            if self.inventory.contains_item(ParcelParams(params.test_condition.test_subject.subject_type, None)):
                item_id = self.inventory.get_first_itemID(params.test_condition.test_subject.subject_type)
                print(f"Retrived item type {params.test_condition.test_subject.subject_type} with ID {item_id}")

                item = ItemFactory.get_item(params.test_condition.test_subject.subject_type, item_id)
                if item == None:
                    print(f"No item {params.test_condition.test_subject.subject_type} with ID {item_id}")
                    return # Should not happen

                print(f"Retrived item {params.test_condition.test_subject.subject_type} with ID {item_id}")
                if hasattr(item, params.test_condition.test_subject.subject_property):
                    print(f"Property {params.test_condition.test_subject.subject_property} has value {getattr(item, params.test_condition.test_subject.subject_property)}")
                    if params.test_condition.test_value == None or getattr(item, params.test_condition.test_subject.subject_property) == params.test_condition.test_value:
                        return
                else:
                    print(f"{params.test_condition.test_subject.subject_type} does not have property: {params.test_condition.test_subject.subject_property}")

            self.cur_instruction += 1 # Skip the next instruction, the condition failed

        match params.test_condition.test_subject.subject_type:
            case "doc":
                InventoryCheck(params)

            case "crate":
                InventoryCheck(params)

            case "cart":
                InventoryCheck(params)

            case "floor":
                raise NotImplementedError
                
            case "building":
                raise NotImplementedError

        return True;

    def InsGoto(self, params):
        if params.label_name in self.labels:
            self.cur_instruction = self.labels[params.label_name]
        else:
            print(f"Unknown label: {params.label_name}")

        return True

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

        self.documents = set()
        self.doc_handling = lambda *_: None

    def tick(self):
        # TODO: Don't tick when we don't need to?

        stopTicking = True
        for doc in self.documents:
            if self.doc_handling(doc) == False:
                stopTicking = False

        pass

    def interact(self, params):
        match params.__class__.__name__:
            case "InsTake":
                if params.parcel_identifier == None:
                    if len(self.documents) :
                        print(f"Docs: {self.documents}")
                        for i in self.documents:
                            self.documents.remove(i)
                            return i
                elif params.parcel_identifier in self.documents:
                    print(f"{self.name} removing {params.parcel_type} {params.parcel_identifier}")
                    self.documents.remove(params.parcel_identifier)
                    return params.parcel_identifier

            case "InsDrop":
                # TODO: Start ticking (when it's not on by default)
                print(f"{self.name} adding {params.parcel_type} {params.parcel_identifier}")
                self.documents.add(params.parcel_identifier)
                return params.parcel_identifier
            case _:
                raise NotImplementedError(params.__class__.__name__)

        return -1
