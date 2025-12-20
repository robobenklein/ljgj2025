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
        self.time_step = 1

    # Load any extra data that should persist untill the level is destroyed
    def setup(self, owner):
        self.desks = arcade.SpriteList()
        self.actors = arcade.SpriteList()
        self.interactables = {}
        self.actor_lookup = {}
        self.owner = owner

        for desk_tobj in self.tile_map.object_lists['desks']:
            print(f"load desk {desk_tobj}")
            desk = Desk()
            self.desks.append(desk)
            desk.setup(desk_tobj)
            self.interactables[desk.name.lower()] = desk

        self.add_sprite_list(
            "Desks",
            sprite_list=self.desks,
            use_spatial_hash=True,
        )

        for actor_tobj in self.tile_map.object_lists['actors']:
            print(f"load actor {actor_tobj}")
            actor = ChalkActor()
            self.actors.append(actor)
            actor.setup(actor_tobj, self)
            self.actor_lookup[actor.name] = actor

        self.add_sprite_list(
            "Actors",
            sprite_list=self.actors,
            use_spatial_hash=False, # actors are expected to move a lot
        )

    # Load any non-persistant data that we don't need to keep around when unloaded
    # Will reset any existing data if called again
    def load(self):
        self.cur_time = 0
        self.tick_count = 0

        for actor_tobj in self.tile_map.object_lists['actors']:
            self.actor_lookup[actor_tobj.name].setup(actor_tobj, self)

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
            if self.time_step == 0 or math.floor(self.cur_time + delta_time) - math.floor(self.cur_time) >= self.time_step:
                self.execution_step()

            self.cur_time += delta_time

    def execution_step(self):
        for desk in self.desks:
            desk.tick()

        for actor in self.actors:
            actor.tick()

        self.tick_count += 1

    def execution_end(self):
        self.running = False
