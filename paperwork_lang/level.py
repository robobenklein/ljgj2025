import arcade
import math

from .assets import levels_dir
from .actor import Desk, ChalkActor


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

    # Load any extra data that should persist until the level is destroyed
    def setup(self, owner):
        self.desks = self.add_sprite_list(
            "Desks",
            use_spatial_hash=True,
        ) # Make now so desks can add more sprites to it, like text on top of them
        self.actors = self.add_sprite_list(
            "Actors",
            use_spatial_hash=False,
        ) # Make now so actors can add more sprites to it, like text that follow them
        self.interactables = {}
        self.actor_lookup = {}
        self.owner = owner

        for desk_tobj in self.tile_map.object_lists['desks']:
            print(f"load desk {desk_tobj}")
            desk = Desk()
            self.desks.append(desk)
            desk.setup(desk_tobj, self)
            self.interactables[desk.name.lower()] = desk     

        for actor_tobj in self.tile_map.object_lists['actors']:
            print(f"load actor {actor_tobj}")
            actor = ChalkActor()
            self.actors.append(actor)
            actor.setup(actor_tobj, self)
            self.actor_lookup[actor.name.lower()] = actor

    # Load any non-persistent data that we don't need to keep around when unloaded
    # Will reset any existing data if called again
    def load(self):
        self.cur_time = 0
        self.tick_count = 0

        for actor_tobj in self.tile_map.object_lists['actors']:
            self.actor_lookup[actor_tobj.name.lower()].setup(actor_tobj, self)

    # Unload anything we don't need to keep
    def unload(self):
        pass

    def execution_start(self):
        self.running = True
        for actor in self.actors:
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
        for interactable in self.interactables.values():
            interactable.tick()

        # Tick actors after so the interactables are not interacted with and update on the same tick
        for actor in self.actor_lookup.values():
            actor.tick()

        self.tick_count += 1

    def execution_end(self):
        self.running = False
