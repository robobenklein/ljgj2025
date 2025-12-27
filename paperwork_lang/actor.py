
import arcade
import lark
import math

from collections import namedtuple
ParcelParams = namedtuple("ParcelParams", ["parcel_type", "parcel_identifier"])

from .assets import assets_dir
from .parser import (
    parse, tree_to_ast, _Instruction, InsDrop
)
from .inventory import ActorInventory

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

        self.angle = 0 # Set before the name_sprite to not trigger two pos sets

        if hasattr(self, 'name_sprite') == False:
            fontSize = 24
            self.name_sprite = arcade.create_text_sprite(f"{tobj.name}", arcade.color.WHITE, fontSize)
            self.name_sprite.hit_box = arcade.hitbox.HitBox([(0,0), (0,0)])
            level.movable_text_sprites.append(self.name_sprite)
        
        # determine position based on the object bounds: (set after the name_sprite so it updates position at the same time)
        assert len(tobj.shape) == 2, "actor map object shape should be 2D spawn point"
        print(f"actor {self.name} at {tobj.shape}")
        self.position = tobj.shape

        assert level.tile_map.tile_width == level.tile_map.tile_height, f"Tile map is not a grid! {level.tile_map.tile_width}/{level.tile_map.tile_height}"
        self.speed = level.tile_map.tile_width / 2 # Move 1/2 tile per tick, provides some angle movement too
        self.barrier_list = arcade.AStarBarrierList(self, level.blocking_sprites, level.tile_map.tile_width,
                                                    level.tile_bounds.left, level.tile_bounds.left + level.tile_bounds.width,
                                                    level.tile_bounds.bottom, level.tile_bounds.bottom + level.tile_bounds.height)
        self.path_points = []

    def load(self, tobj):
        self.center_x = tobj.shape[0]
        self.center_y = tobj.shape[1] # Use center so we don't update text twice
        self.angle = 0
        self.path_points.clear()

    @arcade.Sprite.position.setter
    def position(self, new_value: arcade.Point2):
        arcade.Sprite.position.__set__(self, new_value)
        self.set_name_position()

    @arcade.Sprite.angle.setter
    def angle(self, new_value: float):
        if new_value >= 360:
            new_value -= 360

        arcade.Sprite.angle.__set__(self, new_value)
        self.set_name_position() # Need to update if the angle changed
            
    def load_code_block(self, block):
        """
        Loads the program into the actor and enables execution
        """
        if not block:
            return
        
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

        cur_instruction = 0
        for instruction in self.instructions:
            print(instruction)
            if not isinstance(instruction, _Instruction) and instruction[0] == '#':
                label = instruction.split('#', 1)[1].strip()
                print(f"Adding label: {label}")
                self.labels[label] = cur_instruction

            cur_instruction += 1

    def tick(self):
        if not self.instructions:
            # actor has nothing to do!
            # needs some better indicator of "Idleness"
            # for now let's just spin lol
            self.turn_right(10)
            return
        
        if len(self.path_points) > 0:
            self.move_along_path()
            return

        # runs the current instruction
        if self.cur_instruction >= len(self.instructions):
            self.cur_instruction = 0
            return

        instruction = self.instructions[self.cur_instruction]
        print(f"line {self.cur_instruction} code: {instruction}")
        while not isinstance(instruction, _Instruction):
            self.cur_instruction += 1
            if self.cur_instruction >= len(self.instructions):
                self.cur_instruction = 0
                return

            instruction = self.instructions[self.cur_instruction]
            print(f"line {self.cur_instruction} code: {instruction}")

        # make functions in this class the same as the instruction class name
        if getattr(self, instruction.__class__.__name__)(instruction):
            # if we have finished the command:
            # step the instruction pointer forward
            self.cur_instruction += 1
        else:
            print(f"Actor {self.name} executing instruction {instruction.__class__.__name__}!")

    def set_name_position(self):
        if hasattr(self, "name_sprite"):
            padding = 16
            if self.angle <= 60 or self.angle > 300: # up
                self.name_sprite.position = (self.position[0], self.position[1] + self.height / 2 + padding)
            elif self.angle <= 120 or self.angle > 240: # left/right
                self.name_sprite.position = (self.position[0], self.position[1] + self.width / 4 + padding)
            else: # down
                self.name_sprite.position = (self.position[0], self.position[1] - self.height / 2 - padding)

    def move_along_path(self):
        # Where are we going
        curPoint = self.path_points[self.cur_point]
        destX = curPoint[0]
        destY = curPoint[1]

        # X and Y diff between the two
        xDiff = destX - self.center_x
        yDiff = destY - self.center_y

        # Calculate angle to get there
        angle = math.atan2(yDiff, xDiff)

        # How far are we?
        distance = math.sqrt((self.center_x - destX) ** 2 + (self.center_y - destY) ** 2)

        # How fast should we go? If we are close to our destination,
        # lower our speed so we don't overshoot.
        speed = min(self.speed, distance)

        # Calculate vector to travel
        cos = math.cos(angle)
        sin = math.sin(angle)
        changeX = cos * speed
        changeY = sin * speed

        # Update our location
        self.center_x += changeX
        self.center_y += changeY

        # How far are we?
        distance = math.sqrt((self.center_x - destX) ** 2 + (self.center_y - destY) ** 2)

        # If we are there, head to the next point.
        if distance == 0:
            # Reached the end of the list, start over.
            if self.cur_point == len(self.path_points) - 1:
                print("Arrived at destination")
                self.center_x = destX
                self.center_y = destY
                self.angle = self.end_angle
                self.path_points.clear()
                return
        
            self.cur_point += 1

        self.angle = -round(math.degrees(angle)) # Convert from math's counter clockwise rotations to sprites clockwise rotations

    def InsMove(self, params):
        moveToObj = self.level.item_factory.get_item(params.location_type, params.location_identifier)
        if moveToObj == None:
            print(f"Unable to find {params.location_type} with ID {params.location_identifier} to move actor {self.name} to.")
            return True

        # Get the obj's position, then adjust it by the side we access it from and the actor's height/width
        match moveToObj.__class__.__name__:
            case 'Desk':
                match moveToObj.access_side:
                    case 'top':
                        endPoint = (moveToObj.position.x, moveToObj.bounds.top + self.height / 2)
                        endDirection_degrees = 0
                    case 'bottom':
                        endPoint = (moveToObj.position.x, moveToObj.bounds.bottom - self.height / 2)
                        endDirection_degrees = 180
                    case 'left':
                        endPoint = (moveToObj.bounds.left - self.width / 2, moveToObj.position.y)
                        endDirection_degrees = 270
                    case 'right':
                        endPoint = (moveToObj.bounds.right + self.width / 2, moveToObj.position.y)
                        endDirection_degrees = 90
            # Cart should also have an access side?
            # Box could be any side (but not on it like tutorials)
            case _:
                endPoint = moveToObj.position
                endDirection_degrees = self.angle

        if endPoint != self.position:
            # TODO: This path needs a LOT of smoothing applied and it does not seem to take the sprite's hitbox into account for wall corners...
            #   Time to break out the A* code to fix these common problems
            self.path_points = arcade.astar_calculate_path(self.position, endPoint, self.barrier_list)
            self.cur_point = 1 # Skip the first, it's where we are now
            self.end_angle = endDirection_degrees

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
            case _: # If we are not axis aligned, then we are not at something we can take
                return True

        match params.parcel_type:
            case 'any':
                # TODO: Make list for take/grabables    
                for sprite_list in self.level.interactable_sprites:
                    overlaps = arcade.get_sprites_in_rect(overlapRect, sprite_list)
                    if len(overlaps) > 0:
                        break # Found it 
            
            case 'doc':
                overlaps = arcade.get_sprites_in_rect(overlapRect, self.level.desk_sprites)
                # TODO: Add carts too? Take from a cart of documents? Take an amount of documents?

            case 'tutorial':
                overlaps = arcade.get_sprites_in_rect(overlapRect, self.level.tutorial_sprites)

        if len(overlaps) == 0:
            print(f"Actor {self.name}'s InsTake found no interactables")
            return True

        # TODO: Should only be 1 overlap, but could be a bug later
        interactable = overlaps[0]
        if len(overlaps) > 1:
            print(f"InsTake overlapped with {len(overlaps)} objects! Defaulting to the first right now")

        # TODO: Change to enum or match statement with functions?
        if params.parcel_type == 'doc' or params.parcel_type == 'any':
            if interactable.__class__.__name__ == 'Desk':
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
            elif params.parcel_type != 'any': # Can only take docs from desks
                return True
            # Let 'any' try the other options

        if params.parcel_type == 'tutorial' or params.parcel_type == 'any':
            if interactable.__class__.__name__ == 'Tutorial':
                interactable.interact()
                return True
            # Let 'any' try the other options

        # TODO: Handle other types

    def InsDrop(self, params):
        if self.inventory.contains_item(params) == False:
            print(f"InsDrop actor {self.name} does not contain item {params.parcel_type} with ID {params.parcel_identifier}")
            return True

        # TODO: Handle 'ANY' type
        # Docs must be at a desk to drop them (Don't want to scatter papers all over the floor!)
        if params.parcel_type == 'doc':
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

            # TODO: Make list for doc containers
            overlaps = arcade.get_sprites_in_rect(overlapRect, self.level.desk_sprites)
            if len(overlaps) == 0:
                print(f"InsDrop debug no overlaps")
                return True

            # TODO: Should only be 1 overlap, but could be a bug later
            interactable = overlaps[0]
            if len(overlaps) > 1:
                print(f"InsDrop overlapped with {len(overlaps)} objects! Defaulting to the first right now")

            # If the object can take the document, remove it from our inventory
            if params.parcel_identifier != None:
                if interactable.interact(params) > -1:
                    print(f"{self.name}'s before inventory: {self.inventory.item_map}")
                    self.inventory.remove_item(params)
            else:
                # Specifically need to make a InsDrop so the interactable knows it's getting an item
                newParams = InsDrop(params.parcel_type, self.inventory.get_first_itemID(params.parcel_type))
                if interactable.interact(newParams) > -1:
                    print(f"{self.name}'s before inventory: {self.inventory.item_map}")
                    self.inventory.remove_item(newParams)

            return True

        # TODO: Handle other types

    def InsWhen(self, params):
        def InventoryCheck(params):
            if self.inventory.contains_item(ParcelParams(params.test_condition.test_subject.subject_type, None)):
                item_id = self.inventory.get_first_itemID(params.test_condition.test_subject.subject_type)
                print(f"Retrived item type {params.test_condition.test_subject.subject_type} with ID {item_id}")

                item = self.level.item_factory.get_item(params.test_condition.test_subject.subject_type, item_id)
                if item == None:
                    print(f"No item {params.test_condition.test_subject.subject_type} with ID {item_id}")
                    return # Should not happen

                print(f"Retrived item {params.test_condition.test_subject.subject_type} with ID {item_id}")
                if hasattr(item, params.test_condition.test_subject.subject_property):
                    subjProp = getattr(item, params.test_condition.test_subject.subject_property)
                    if hasattr(subjProp, "lower"):
                        subjProp = subjProp.lower()
                        
                    print(f"Property {params.test_condition.test_subject.subject_property} has value {subjProp}")
                    if params.test_condition.test_value == None or subjProp == params.test_condition.test_value:
                        return
                else:
                    print(f"{params.test_condition.test_subject.subject_type} does not have property: {params.test_condition.test_subject.subject_property}")

            self.cur_instruction += 1 # Skip the next instruction, the condition failed

        match params.test_condition.test_subject.subject_type:
            case 'doc':
                InventoryCheck(params)

            case 'crate':
                InventoryCheck(params)

            case 'cart':
                InventoryCheck(params)

            case 'floor':
                raise NotImplementedError
                
            case 'building':
                raise NotImplementedError

        return True

    def InsGoto(self, params):
        if params.label_name in self.labels:
            self.cur_instruction = self.labels[params.label_name]
        else:
            print(f"Unknown label: {params.label_name}, labels: {self.labels}")

        return True
