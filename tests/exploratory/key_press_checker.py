"""Only works for speical keys? It doesn't work at all for me"""
import os
import time

import sys
sys.path.append("../../cave_dweller")
import libtcodpy as libtcod 

from game import Game
import util


font_size_index = 2
libtcod.console_set_custom_font(util.game_path(os.path.join('fonts', 'dejavu16x16_gs_tc.png')), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(Game.screen_width, Game.screen_height, 'Cave Dweller', libtcod.RENDERER_GLSL)
libtcod.sys_set_fps(40)
key = libtcod.Key()
mouse = libtcod.Mouse()
while True:
    while True:
        libtcod.sys_check_for_event(libtcod.EVENT_ANY,key,mouse)
        #print "%r %r" % (key.vk, key.c)
        if key.c != 0 and key.vk != 0:
            print "c: %r, vk: %r; pressed: %r; lalt: %r; ralt: %r; lctrl: %r; rctrl: %r; shift: %r;" % (key.c, key.vk, key.pressed, key.lalt, key.ralt, key.lctrl, key.rctrl, key.shift)
        if key.vk == libtcod.KEY_NONE:
            break
    libtcod.console_flush()
