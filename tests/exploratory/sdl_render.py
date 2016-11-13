"""I got sys_register_SDL_renderer to work!"""
import time
import sys
import os
sys.path.append("../../cave_dweller")

import libtcodpy as libtcod
from ctypes import *

import draw_text

def render(surface):
    draw_text.draw_text("it works!", surface, 25, 25)
    #sdl.fill_circle(surface, 1, 1, 5, 5)


libtcod.console_set_custom_font(os.path.join('../../fonts', 'dejavu12x12_gs_tc.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(90,40, 'test', False, libtcod.RENDERER_SDL)
# Set font size, init ttf
draw_text.set_font(pt_size=12)
libtcod.sys_register_SDL_renderer(render)
libtcod.sys_set_fps(40)
libtcod.console_flush()
time.sleep(10)
