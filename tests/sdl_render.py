"""As of now sdl surfaces do not work"""
import time
import sys
import os
sys.path.append("cave_dweller")

import libtcodpy as libtcod
import pygame
from pygame.locals import *

def render(my_surface):
    import pdb; pdb.set_trace()
    pygame.draw.circle(my_surface, pygame.Color(155, 155, 155), (100,100), 100)

libtcod.console_set_custom_font(os.path.join('fonts', 'dejavu12x12_gs_tc.png'), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(90,40, 'test', False, libtcod.RENDERER_SDL)
libtcod.sys_register_SDL_renderer(render)
libtcod.sys_set_fps(40)
libtcod.console_flush()
time.sleep(10)
