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
prev_str = ""
while True:
    while True:
        libtcod.sys_check_for_event(libtcod.EVENT_ANY,key,mouse)
        #print "%r %r" % (key.vk, key.c)
        my_str =  "x: %r; y: %r; dx: %r; dy: %r; cx: %r; cy: %r; dcx: %r; dcy: %r; lbtn: %r; rbtn: %r; mbtn: %r; lbtn_pressed: %r; rbtn_pressed: %r; mbtn_pressed: %r; whl_up: %r; whl_down: %r" % (mouse.x, mouse.y, mouse.dx, mouse.dy, mouse.cx, mouse.cy, mouse.dcx, mouse.dcy, mouse.lbutton, mouse.rbutton, mouse.mbutton, mouse.lbutton_pressed, mouse.rbutton_pressed, mouse.mbutton_pressed, mouse.wheel_up, mouse.wheel_down)
        if my_str != prev_str:
            print(my_str)
        prev_str = my_str
        if key.vk == libtcod.KEY_NONE:
            break
    libtcod.console_flush()
