"""Only works for speical keys? It doesn't work at all for me"""
import os
import time

import sys
sys.path.append("cave_dweller")
import libtcodpy as libtcod 

from game import Game


font_size_index = 2
libtcod.console_set_custom_font(os.path.join('fonts', 'dejavu16x16_gs_tc.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(Game.screen_width, Game.screen_height, 'Cave Dweller', libtcod.RENDERER_GLSL)
libtcod.sys_set_fps(40)
while True:
    print(libtcod.console_is_key_pressed(libtcod.KEY_UP))
    libtcod.console_flush()
