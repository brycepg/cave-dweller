import os

import sys
sys.path.append('cave_dweller')
import libtcodpy as libtcod

from game import Game

font_size_index = 0
libtcod.console_set_custom_font(os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'.format(size=Game.font_sizes[font_size_index])), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(Game.screen_width, Game.screen_height, 'Cave Dweller', libtcod.RENDERER_GLSL)
libtcod.console_set_default_background(0,libtcod.red)
mouse_con = libtcod.console_new(Game.screen_width, Game.screen_height)
libtcod.console_set_default_background(mouse_con,None)
libtcod.sys_set_fps(40)
mouse = libtcod.Mouse()
libtcod.mouse_show_cursor(False)
key = libtcod.Key()
while True:
    libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse)
    print((mouse.cx, mouse.cy))
    print(libtcod.console_has_mouse_focus())
    libtcod.console_clear(0)
    libtcod.console_clear(mouse_con)
    libtcod.console_put_char_ex(0, 10, 10, ord(' '), None, libtcod.black)
    # There's a bug where has mouse focus returns true if the mouse starts on 
    # the console. (hence the edge checks)
    if libtcod.console_has_mouse_focus() or ((mouse.cx != 0 and mouse.cy != 0) and (mouse.cx != 0 and mouse.cy != Game.screen_height-1) and (mouse.cx != Game.screen_width-1 and mouse.cy != Game.screen_height-1) and (mouse.cx != Game.screen_width-1 and mouse.cy != 0)):
        libtcod.console_put_char_ex(mouse_con, mouse.cx, mouse.cy, ord('x'), libtcod.yellow, None)
    #console_blit(src,xSrc,ySrc,xSrc,hSrc,dst,xDst,yDst,foregroundAlpha=1.0,backgroundAlpha=1.0)
    libtcod.console_blit(mouse_con, x=0, y=0, w=0, h=0, dst=0, xdst=0, ydst=0, ffade=.75, bfade=.0)
    libtcod.console_flush()
