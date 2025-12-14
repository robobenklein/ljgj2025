
from pathlib import Path
import random
import arcade
import arcade.gui

from .assets import assets_dir
from .levels.mainmenu import MenuLevel


class MainMenu(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.physics_engine = None

        self.camera_world = arcade.Camera2D()
        self.camera_gui = arcade.Camera2D()

        self.background = arcade.load_texture(assets_dir / 'chalkboard-512-dark1.png')
        # how to tile this idk
        # self.background.

        self.static_visuals = arcade.SpriteList()

        title_logo = arcade.Sprite(
                assets_dir / 'chalk-CPU-logo-leftalign.png',
                scale=0.5,
                # center_x=350/2,
                # center_y=1080-(270/2)
        )
        self.title_logo = arcade.gui.UISpriteWidget(
            sprite=title_logo,
            width=title_logo.width,
            height=title_logo.height
        )

        # main box separates code input / menuing from the gameplay board on the right
        self.boxLR = arcade.gui.UIBoxLayout(
            vertical=False,
            # The menuBox should not grow, but the playBox will
            # the boxLR will take the whole viewport
            size_hint=(1, 1)
        )
        self.menuBox = arcade.gui.UIBoxLayout(
            vertical=True,
            # take the whole vertical space, don't horiztonally
            size_hint=(0,1)
        )
        self.menuBox.add(self.title_logo)
        self.playBox = arcade.gui.UIBoxLayout(
            vertical=True,
            # fill remaining space
            size_hint=(1,1),
        )

        self.boxLR.add(self.menuBox)
        self.boxLR.add(self.playBox)

        self.dbg1btn = arcade.gui.UIFlatButton(
            text="Debug 1",
        )
        self.dbg2btn = arcade.gui.UIFlatButton(
            text="Debug 2",
        )
        self.menuBox.add(self.dbg1btn)
        self.menuBox.add(self.dbg2btn)

        @self.dbg1btn.event("on_click")
        def on_click_dbg1(event: arcade.gui.UIOnClickEvent):
            self.camera_world.position = self.level.player.position
            print(f"WorldCam f{self.camera_world.position}")
            # self.camera_world.position -= (100, 100)

        # for the main menu play area, we'll take in lines of code like a shell prompt:
        self.code_input = arcade.gui.UIInputText(
            size_hint=(1, 0.1),
        )
        # and it will control a 'player character',
        self.camera_world_space = arcade.gui.UISpace(
            size_hint=(1, 1),
        )
        
        self.playBox.add(self.camera_world_space)
        self.playBox.add(self.code_input)

        # get this whole layout on screen
        self.anchor = self.manager.add(arcade.gui.UIAnchorLayout())
        self.anchor.add(
            anchor_x="center_x",
            anchor_y="center_y",
            child=self.boxLR
        )

        self.level = MenuLevel.factory()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)
        self._o_x, self._o_y = random.randrange(0, 512), random.randrange(0, 512)
        
        self.manager.execute_layout()
        self.manager.debug()
        self.level.setup()

        # self.play_camera.viewport = self.camera_space.rect
        self.camera_world.update_values(self.camera_world_space.rect)
        # self.ui.camera.position = (
        #     self.camera_space.rect.x * 2,
        #     self.camera_space.rect.y * 2,
        # )
        print(f"CWS rect {self.camera_world_space.rect}")
        self.camera_world.position -= (
            self.camera_world_space.rect.left,
            self.camera_world_space.rect.bottom,
        )

        # self.camera_world.projection = arcade.LBWH(
        #     -1920, -1080, 1920, 1080,
        # )

        print(self.camera_world.position)

        print(f"World camera viewport: {self.camera_world.viewport}")
        print(f"World camera position: {self.camera_world.position}")

        print(self.camera_world.point_in_view(self.level.player.position))

    def on_hide_view(self):
        self.manager.disable()

    def on_draw_before_ui(self):
        # self.play_camera.use()
        raise NotImplementedError()

    def draw_background(self):
        self.camera_gui.use()
        draw_target_space = arcade.LBWH(
            0,
            0,
            self.boxLR.rect.width,
            900,
        )
        arcade.draw_lbwh_rectangle_outline(
            *(draw_target_space.lbwh),
            border_width=5,
            color=arcade.color.WHITE,
        )

        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                0,
                0,
                1920,
                1080
            )
        )

    def on_draw(self):
        self.clear()

        # Draw background
        self.draw_background()
        # arcade.draw_texture_rect(
        #     self.background,
        #     arcade.LBWH(-self._o_x, -self._o_y, 1920+self._o_x, 1080+self._o_y)
        # )

        # Do game world rendering first
        self.camera_world.use()
        self.level.draw()
        self.level.draw_hit_boxes(
            color=(255, 0, 255, 255),
        )

        # now draw gui
        self.camera_gui.use()
        self.manager.draw()