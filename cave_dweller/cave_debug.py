import collections
import operator

import libtcodpy as libtcod

from context_menu import ContextMenu
from game import Game

# Check object types
def display_cur_objects(world):
    count = collections.Counter([type(obj).__name__ for aos in world.blocks.values() for obj in aos.objects])
    return count

def obj_type_per_block(world):
    count = {}
    for key in world.blocks:
        count[key] = collections.Counter([type(obj).__name__ for obj in world.blocks[key].objects])

    return count

# Num objects per block
def num_obj_per_block(world):
    return {key: len(value.objects) for key, value in world.blocks.items()}

def get_locs(block, class_type=None):
    objects = block.objects
    coords = {}
    for a_object in objects:
        if class_type:
            if not isinstance(a_object, class_type):
                continue
        coords[(a_object.x, a_object.y)] = type(a_object).__name__

    return coords
    #key_sort = sorted(coords.keys(), key=operator.itemgetter(1,2))
    #for key in key_sort:
    #    print("{}: {}".format(key, coords[key]))

def debug_print(args):
    """Pass locals of main loop to print debug information"""
    exec("") # Avoid locals optimization to allow locals update hack
    locals().update(args)
    libtcod.console_print(Game.debug_con, 1, 1, "FPS: %s" % (str(int(1/fps_base))))
    libtcod.console_print(Game.debug_con, 1, 2, "blocks: %d" % len(world.blocks))
    libtcod.console_print(Game.debug_con, 1, 3, "block: (%d,%d)" % (game.idx_cur, game.idy_cur))
    libtcod.console_print(Game.debug_con, 1, 4, "view: (%dx%d)" % (game.view_x, game.view_y))
    libtcod.console_print(Game.debug_con, 1, 5, "player: (%dx%d)" % (player.x, player.y))
    libtcod.console_print(Game.debug_con, 1, 6, "process/draw time: ({0:.4f})".format(spent_time))
    num_objects = sum([len(block.objects) for block in world.blocks.values()])
    libtcod.console_print(Game.debug_con, 1, 7, "objects: {}".format(num_objects))

def debug_menu(key, debug_info, world):
    """Show some stats for object overseeing"""
    import cave_debug
    if key.lctrl and key.pressed and key.c == ord('q') and Game.debug:
        if not debug_info:
            debug_info = ContextMenu(Game.game_width, 0, height=Game.screen_height, width=Game.screen_width-Game.game_width)
        elif debug_info:
            debug_info.clear()
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
