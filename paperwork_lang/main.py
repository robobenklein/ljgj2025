#!/usr/bin/env python3

import arcade
import random
from .cpu_game import GameplayView


WINDOW_TITLE = "Central Paperwork Unit"

def main():
    # TODO settings load?
    window = arcade.Window(
        width=1920,
        height=1080,
        title=WINDOW_TITLE,
        fullscreen=False,
        resizable=False,
        vsync=True
    )

    game = GameplayView()
    # game.setup()
    window.show_view(game)
    arcade.run()


if __name__ == '__main__':
    main()
