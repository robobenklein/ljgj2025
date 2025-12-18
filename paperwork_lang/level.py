import arcade
from .assets import levels_dir
from .actor import Desk


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
        return new

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.running = False
        self.tile_map = None

    def setup(self):
        self.desks = arcade.SpriteList()
        self.interactables = {}

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

    def execution_start(self):
        raise NotImplementedError()

    def execution_tick(self):
        if self.running:
            self.execution_step()

    def execution_step(self):
        for desk in self.desks:
            desk.tick()

    def execution_end(self):
        raise NotImplementedError()