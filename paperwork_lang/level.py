import arcade
import math

from .assets import levels_dir
from .actor import ChalkActor
from .itemfactory import ItemFactory

class ChalkLevel(arcade.Scene):
    """
    A ChalkBoard level:
    Commonalities include a set of Desks, actors, a Tiled map, etc.
    """
    @classmethod
    def factory(cls):
        if not hasattr(cls, 'level_filename'):
            raise NotImplementedError(f"no level_filename for {cls}")
        layer_options = {}
        tile_map = arcade.load_tilemap(
            levels_dir / cls.level_filename,
            layer_options=layer_options,
            use_spatial_hash=True,
            hit_box_algorithm=arcade.hitbox.SimpleHitBoxAlgorithm(),
        )
        new = cls.from_tilemap(
            tile_map,
        )
        new.tile_map = tile_map
        new.tile_bounds = arcade.LBWH(
            0,
            0,
            tile_map.width * tile_map.tile_width,
            tile_map.height * tile_map.tile_height,
        )
        return new

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.tile_map = None
        self.tile_bounds = None
        self.time_step = .5 # every 60 frames seems too slow TODO: (possibly make it an option in a button)
        self.item_factory = ItemFactory()

    # Load any extra data that should persist until the level is destroyed
    def setup(self, owner):
        self.desk_sprites = self.add_sprite_list(
            'Desks',
            use_spatial_hash=True,
        )
        self.text_sprites = self.add_sprite_list(
            'Text',
            use_spatial_hash=True,
        )

        self.interactable_sprites = []
        self.interactable_sprites.append(self.desk_sprites)

        self.movable_text_sprites = self.add_sprite_list('movable_text')
        self.owner = owner

        for item_type in self.item_factory.constructors:
            pluralType = f"{item_type}s"
            if pluralType in self.tile_map.object_lists:
                print(f"Setup {pluralType}")
                self.item_factory.factory(self.tile_map.object_lists[pluralType], level=self)

        building_sprites = self.tile_map.sprite_lists['building']
        self.blocking_sprites = arcade.SpriteList(True, 128, None, len(building_sprites) + len(self.desk_sprites), True, False) # TODO: Add more types?
        self.blocking_sprites.extend(iter(building_sprites))
        self.blocking_sprites.extend(iter(self.desk_sprites))

        # Setup actors last as they need all the other sprites for pathing
        self.actor_sprites = self.add_sprite_list('Actors')
        self.actors = {}
        for actor_tobj in self.tile_map.object_lists['actors']:
            print(f"Setup actor {actor_tobj}")
            actor = ChalkActor()
            self.actor_sprites.append(actor)
            actor.setup(actor_tobj, self)
            self.actors[actor.name.lower()] = actor

    # Load any non-persistent data that we don't need to keep around when unloaded
    # Will reset any existing data if called again
    def load(self):
        self.cur_time = 0
        self.tick_count = 0

        for actor_tobj in self.tile_map.object_lists['actors']:
            self.actors[actor_tobj.name.lower()].load(actor_tobj) # Reload any dynamic data for the actor, position angle etc.

        self.item_factory.load_items(self.tile_map.object_lists) # Reload any dynamic data for the items, position functionality (spawning) etc.

    # Unload anything we don't need to keep
    def unload(self):
        pass
        
    def execution_start(self):
        self.running = True
        for actor in self.actors.values():
            actor.load_code_block(actor.saved_code_block)

    def execution_tick(self, delta_time):
        if self.running:
            # TODO: Once we have path finding, move this to objects themselves (like desks) to simulate processing time
            # We don't want to tick too fast or actions go by too quick (and faster frame rate = faster code)
            timeCheck = self.cur_time - self.tick_count * self.time_step 
            if self.time_step == 0 or (timeCheck + delta_time) - math.floor(timeCheck) >= self.time_step:
                self.execution_step()

            self.cur_time += delta_time

    def execution_step(self):
        for desk in self.item_factory.get_items('desk').values():
            desk.tick()

        # Tick actors after so the interactables are not interacted with and update on the same tick
        for actor in self.actors.values():
            actor.tick()

        self.tick_count += 1

    def execution_end(self):
        self.running = False
