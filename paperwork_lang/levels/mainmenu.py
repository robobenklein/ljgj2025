
import arcade

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor, Desk

class PlayerActor(ChalkActor):
    def __init__(self):
        super().__init__(
            assets_dir / "char1.png",
            # assets_dir / "chalk-desk1.png",
            scale=1/4,
        )

class MenuLevel(arcade.Scene):
    @classmethod
    def factory(cls):
        layer_options = {}
        tile_map = arcade.load_tilemap(
            levels_dir / 'menu1.json',
            layer_options=layer_options,
            use_spatial_hash=True,
            hit_box_algorithm=arcade.hitbox.SimpleHitBoxAlgorithm(),
        )
        new = cls.from_tilemap(
            tile_map,
        )
        new.tile_map = tile_map
        return new

    def setup(self):
        self.player = PlayerActor()

        self.add_sprite(
            "Player",
            self.player
        )

        self.player.position = (100, 100)

        self.desks = arcade.SpriteList()
        for desk_tobj in self.tile_map.object_lists['desks']:
            print(f"load desk {desk_tobj}")
            desk = Desk()
            self.desks.append(desk)
            desk.setup(desk_tobj)

        self.add_sprite_list(
            "Desks",
            sprite_list=self.desks,
            use_spatial_hash=True,
        )