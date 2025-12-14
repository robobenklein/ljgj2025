
import arcade

from ..assets import assets_dir, levels_dir
from ..actor import ChalkActor

class PlayerActor(ChalkActor):
    def __init__(self):
        super().__init__(
            assets_dir / "char1.png",
            scale=1/4,
        )

class MenuLevel(arcade.Scene):
    @classmethod
    def factory(cls):
        layer_options = {
            "Platforms": {
                "use_spatial_hash": True,
            },
        }
        tile_map = arcade.load_tilemap(
            levels_dir / 'menu1.json',
            layer_options=layer_options,
        )
        return cls.from_tilemap(
            tile_map,
        )

    def setup(self):
        self.player = PlayerActor()

        # self.add_sprite(
        #     "Player",
        #     self.player
        # )

        self.player.position = (100, 100)