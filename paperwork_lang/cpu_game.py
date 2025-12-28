
import random
import arcade
import arcade.gui
import pyperclip
import keyboard

from .assets import assets_dir, starter_code
from .levels.mainmenu import MenuLevel
from .levels.level1 import Level1

from .statestack import StateStack

class GameplayView(arcade.View):
    def __init__(self):
        super().__init__()

        self.manager = arcade.gui.UIManager()
        self.manager.enable()
        self.physics_engine = None
        # whether the render update loop will call game ticking or not:
        self.ticking_realtime = False
        self.active_level_class = MenuLevel

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
            # take the whole vertical space, don't horizontally
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
            text="Snap->Player",
        )
        self.dbg2btn = arcade.gui.UIFlatButton(
            text="Level 1",
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
            if self.ticking_start.text == "Start" and not self.level.running:
                currentActor = self.current_input_actor_name.lower()
                if currentActor in self.level.actors:
                    # Save the block so it can be loaded on execution 
                    self.level.actors[currentActor].saved_code_block = self.code_editor_actor.text

            self.start_realtime_ticking()

        self.ticking_once = arcade.gui.UIFlatButton(
            text="Step",
        )
        @self.ticking_once.event("on_click")
        def on_click_once(event: arcade.gui.UIOnClickEvent):
            currentActor = self.current_input_actor_name.lower()
            if currentActor in self.level.actors:
                    # Save the block so it can be loaded on execution 
                    self.level.actors[currentActor].saved_code_block = self.code_editor_actor.text

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
            if hasattr(self, "player") and self.camera_world.position != self.level.player.position:
                self.camera_world.position = self.level.player.position
            else:
                self.camera_world.position = self.level.tile_bounds.center

            print(f"WorldCam f{self.camera_world.position}")
            # self.camera_world.position -= (100, 100)

        @self.dbg2btn.event("on_click")
        def on_click_dbg2(event: arcade.gui.UIOnClickEvent):
            if self.level.__class__ != Level1:
                self.add_level(Level1)
            else:
                self.remove_current_level()

        # for the main menu play area, we'll take in lines of code like a shell prompt:
        self.code_input = arcade.gui.UIInputText(
            size_hint=(1, 0.1),
            caret_color=arcade.color.WHITE,
            text="# This is your character's control input box, press enter to execute a command"
        )
        @self.code_input.event("on_change")
        def on_code_input_change(event: arcade.gui.UIOnChangeEvent):
            self.handle_code_input(event)

        self.current_input_actor_name = ""
        self.current_input_actor_UI = arcade.gui.UITextWidget(
            size_hint=(1, 0.1),
            text="Currently editing actor: NONE"
        )
        self.menuBox.add(self.current_input_actor_UI)

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
        self.camera_world_space = arcade.gui.UIAnchorLayout(
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
        
        # Make the menu level that will always persist
        self.level = MenuLevel.factory()
        self.level.setup(self)
        self.level_stack = StateStack(self.level)

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
        # TODO: Replace with arcade.Window.on_key_press()
        if keyboard.is_pressed("ctrl") and keyboard.is_pressed("v"):
            print(pyperclip.paste())
            self.code_editor_actor.text = pyperclip.paste()
    
        if self.ticking_realtime:
            self.level.execution_tick(delta_time)

    def handle_code_input(self, event: arcade.gui.UIOnChangeEvent):
        """
        Runs a single command entered in the player's control box
        """
        print(f"text input change: {event}")
        if '\n' in event.new_value:
            # TODO better "execute command" detection, use the Window.on_key_press() for enter?
            # TODO: Handle tab for autocomplete?
            self.code_input.text = event.old_value
        else:
            # nothing to execute here
            return

        try:
            self.level.player.load_code_block(event.old_value)
            # TODO some commands might take multiple ticks,
            # should keep ticking until instruction pointer advances or loops back
            self.level.execution_step()
        except Exception as e:
            # TODO handle bad code
            raise e

    def on_mouse_press(self, x, y, button, key_modifiers):
        """
        Called when the user presses a mouse button.
        """
        # TODO: This may be conflicting with closing the popup?
        if button == arcade.MOUSE_BUTTON_LEFT:
            worldLocation = self.camera_world.unproject((x, y))
            if (worldLocation.x, worldLocation.y) in self.level.tile_bounds:
                overlaps = arcade.get_sprites_in_rect(arcade.XYWH(worldLocation.x, worldLocation.y, 10, 10), self.level.actor_sprites)
                if len(overlaps):
                    if self.current_input_actor_name != "" and overlaps[0].name != self.current_input_actor_name:
                        # Save the code to the actor before we change to a new one
                        self.level.actors[self.current_input_actor_name.lower()].saved_code_block = self.code_editor_actor.text

                    self.current_input_actor_name = overlaps[0].name
                    self.current_input_actor_UI.text = f"Currently editing actor: {self.current_input_actor_name}"
                else:
                    self.current_input_actor_name = ""
                    self.current_input_actor_UI.text = "Currently editing actor: NONE"

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
        self.level.execution_tick(1) # Assuming perfect 60 fps since we are stepping

    def start_level_execution(self):
        # load actor code into actors...
        self.level.execution_start()
        self.level.running = self.ticking_realtime

    def on_reset(self, event: arcade.gui.UIOnClickEvent):
        self.level.execution_end()
        self.reset_level()

    def reset_level(self):
        self._o_x, self._o_y = random.randrange(0, 512), random.randrange(0, 512)

        self.ticking_realtime = False
        self.ticking_start.text = "Start"

        self.camera_world.update_values(self.camera_world_space.rect)
        # move the camera so we can see the whole level now:
        print(f"CWS rect {self.camera_world_space.rect}")
        # find the center of the level and move the camera there first:
        self.camera_world.position = self.level.tile_bounds.center
        print(f"Camera moved to gamespace {self.camera_world.position}")
        # figure out camera zoom so that we fit the level in viewport:
        self.camera_world.zoom = min(
            self.camera_world_space.rect.width / self.level.tile_bounds.width,
            self.camera_world_space.rect.height / self.level.tile_bounds.height,
        )

        print(f"World camera viewport: {self.camera_world.viewport}")
        print(f"World camera position: {self.camera_world.position}")

        # Reload any non-persistent data
        self.level.load()

    def add_level(self, level):
        self.level = level.factory()
        self.level.setup(self)
        print(f"Moving to level: {self.level}")      
        self.level_stack.push_state(self.level)
        self.reset_level()
        
    def remove_current_level(self):
        self.level.execution_end()
        self.level.running = False
        print(f"Moving from level: {self.level}")
        self.level = self.level_stack.pop_state()
        print(f"To level: {self.level}")
        self.reset_level()
