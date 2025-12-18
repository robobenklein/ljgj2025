
from pathlib import Path
import random
import arcade
import arcade.gui

from .assets import assets_dir, starter_code
from .levels.mainmenu import MenuLevel


class GameplayView(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.physics_engine = None
        # whether the render update loop will call game ticking or not:
        self.ticking_realtime = False

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

        ### TICKING controls section
        self.tickControls = arcade.gui.UIBoxLayout(
            vertical=False,
            # take whole horizontal space
            size_hint=(1, 0),
        )
        self.ticking_start = arcade.gui.UIFlatButton(
            text="Start",
        )
        @self.ticking_start.event("on_click")
        def on_click_start(event: arcade.gui.UIOnClickEvent):
            self.start_realtime_ticking()
        self.ticking_once = arcade.gui.UIFlatButton(
            text="Step",
        )
        @self.ticking_once.event("on_click")
        def on_click_once(event: arcade.gui.UIOnClickEvent):
            self.do_single_tick()
        self.ticking_stop = arcade.gui.UIFlatButton(
            text="Reset",
        )
        @self.ticking_stop.event("on_click")
        def on_click_stop(event: arcade.gui.UIOnClickEvent):
            self.on_reset(event)
        for btn in (self.ticking_start, self.ticking_once, self.ticking_stop):
            self.tickControls.add(btn)
        self.menuBox.add(self.tickControls)
        ### END TICKING controls section

        @self.dbg1btn.event("on_click")
        def on_click_dbg1(event: arcade.gui.UIOnClickEvent):
            self.camera_world.position = self.level.player.position
            print(f"WorldCam f{self.camera_world.position}")
            # self.camera_world.position -= (100, 100)

        # for the main menu play area, we'll take in lines of code like a shell prompt:
        self.code_input = arcade.gui.UIInputText(
            size_hint=(1, 0.1),
            caret_color=arcade.color.WHITE,
            text="# This is your character's control input box, press enter to execute a command"
        )
        @self.code_input.event("on_change")
        def on_code_input_change(event: arcade.gui.UIOnChangeEvent):
            self.handle_code_input(event)

        # to program the actors, the editor goes in the left column
        # in the future you might open one on the right too?
        # (to edit multiple actors' code)
        self.code_editor_actor = arcade.gui.UIInputText(
            # takes all the remaining space:
            size_hint=(1, 1),
            multiline=True,
            text=starter_code["mainmenu"],
            caret_color=arcade.color.WHITE,
        )
        self.menuBox.add(self.code_editor_actor)

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

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        self.manager.execute_layout()
        self.manager.debug()

        self.reset_level()

    def center_camera_to_level(self):
        pass # TODO

    def on_hide_view(self):
        self.manager.disable()

    def on_draw_before_ui(self):
        # self.play_camera.use()
        raise NotImplementedError()

    def draw_background(self):
        """
        TODO; this should tile the chalkboard with a random offset
        """
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
        """
        keep this function minimal
        it runs on every *frame*, not just game ticks
        for game logic it's in on_update()
        if this were a fully released game, some interpolation of movement might happen here too
        """
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

    def on_update(self, delta_time: float):
        if self.ticking_realtime:
            self.level.execution_tick()

    def handle_code_input(self, event: arcade.gui.UIOnChangeEvent):
        """
        Runs a single command entered in the player's control box
        """
        print(f"text input change: {event}")
        if '\n' in event.new_value:
            # TODO better "execute command" detection
            self.code_input.text = event.old_value
        else:
            # nothing to execute here
            return

        try:
            self.level.player.load_code_block(event.old_value)
            # TODO some commands might take multiple ticks,
            # should keep ticking until instruction pointer advances or loops back
            self.level.execution_step()
            # if successful, consume the command
            self.code_input.text = ""
        except Exception as e:
            # TODO handle bad code
            raise e

    def start_level_execution(self):
        # load actor code into actors...
        self.level.execution_start()
        self.level.running = self.ticking_realtime

    def start_realtime_ticking(self, realtime=None):
        """
        Called as Start/Pause button action
        """
        if realtime == None:
            self.ticking_realtime = not self.ticking_realtime
        else:
            self.ticking_realtime = realtime
        self.ticking_start.text = "Pause" if self.ticking_realtime else "Start"
        if self.ticking_realtime and not self.level.running:
            self.start_level_execution()

    def do_single_tick(self):
        if self.ticking_realtime:
            # pause execution
            # HACK to just pretend the button was pressed lol
            self.start_realtime_ticking(False)
        if not self.level.running:
            self.level.execution_start()
        self.level.execution_tick()

    def on_reset(self, event: arcade.gui.UIOnClickEvent):
        self.level.execution_end()
        self.level.running = False
        self.reset_level()

    def reset_level(self):
        self._o_x, self._o_y = random.randrange(0, 512), random.randrange(0, 512)

        # TODO make a new instance of the currently selected level,
        # not just the main menu level
        self.level = MenuLevel.factory()
        self.level.setup()

        self.ticking_realtime = False
        self.ticking_start.text = "Start"

        # self.play_camera.viewport = self.camera_space.rect
        self.camera_world.update_values(self.camera_world_space.rect)
        # self.ui.camera.position = (
        #     self.camera_space.rect.x * 2,
        #     self.camera_space.rect.y * 2,
        # )
        print(f"CWS rect {self.camera_world_space.rect}")
        # self.camera_world.position -= (
        #     self.camera_world_space.rect.left,
        #     self.camera_world_space.rect.bottom,
        # )

        # self.camera_world.projection = arcade.LBWH(
        #     -1920, -1080, 1920, 1080,
        # )

        print(self.camera_world.position)

        print(f"World camera viewport: {self.camera_world.viewport}")
        print(f"World camera position: {self.camera_world.position}")

        print(self.camera_world.point_in_view(self.level.player.position))
