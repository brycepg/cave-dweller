import os
import time

import sys
sys.path.append("cave_dweller")
import libtcodpy as libtcod 

from game import Game


font_size_index = 2
libtcod.console_set_custom_font(os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'.format(size=Game.font_sizes[font_size_index])), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(Game.screen_width, Game.screen_height, 'Cave Dweller', libtcod.RENDERER_GLSL)
libtcod.sys_set_fps(40)
for num in range(127):
    #libtcod.console_set_char(0, num % Game.screen_width, num // Game.screen_height, num)
    msg = str(num) + ":" + chr(num)
    msg = "a"
    #libtcod.console_print(0, (num*len(msg)) % (Game.screen_width), (num*len(msg)) // (Game.screen_height), msg) 
    libtcod.console_print(0, (num) % (Game.screen_width), num // (Game.screen_height), chr(num)) 
libtcod.console_print(0, 1, 10, chr(24))
libtcod.console_print(0, 1, 11, chr(25))
libtcod.console_flush()

time.sleep(10)
