import re

import libtcodpy as libtcod

from game import Game

class ContextMenu:
    def __init__(self, x=0, y=0, width=20, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cur_line = 0
        self.con = libtcod.console_new(width, height)
        text = []

    def write(self, text):
        if self.cur_line < self.height:
            libtcod.console_print(self.con, 0, self.cur_line, text)
            self.cur_line += 1

    def draw(self):
        libtcod.console_blit(self.con, 0, 0, 0, 0, 0, self.x, self.y)

    def clear(self):
        self.cur_line = 0
        libtcod.console_clear(0)
        libtcod.console_clear(self.con)

def debug_menu(key, debug_info, world):
    """Show some stats for object overseeing"""
    import cave_debug
    if key.lctrl and key.pressed and key.c == ord('q') and Game.debug:
        if not debug_info:
            debug_info = ContextMenu(Game.game_width, 0, height=Game.screen_height, width=Game.screen_width-Game.game_width)
            #windows.append(debug_info)
        elif debug_info:
            #con = windows.pop(0)
            debug_info.clear()
            #con.clear()
            libtcod.console_delete(debug_info.con)
            debug_info = None
    if debug_info:
        debug_info.clear()
        debug_info.write("Number of objects per block")
        for key, value in cave_debug.num_obj_per_block(world).items():
            text = "%s: %s" % (key, value)
            debug_info.write(text)
        debug_info.write("")
        debug_info.write("Current object type count")
        for key, value in cave_debug.display_cur_objects(world).items():
            text = "%s: %s" % (key, value)
            debug_info.write(text)
        debug_info.write("")
        debug_info.write("Num of object per block")
        for key, value in cave_debug.num_obj_per_block(world).items():
            text = "%s: %s" % (key, value)
            debug_info.write(text)
        debug_info.draw()
    return debug_info
