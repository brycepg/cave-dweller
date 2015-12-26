#!/usr/bin/env python2
""" Call this file to start the game
Stores initalization of game, main game loop
And command-line argument processing
"""

__author__ = "Bryce Guinta"
__contact__ = "azrathud@gmail.com"
__version__ = "0.0.5"

import argparse
import sys
import time
import os
import logging
import collections

import libtcodpy as libtcod 

import menu
import mouse_handler
import status_handler
from game import Game
from world import World
from world import GetOutOfLoop
from objects import Player
from menu import Menu
import actions
import context_menu
from serializer import Serializer

log = logging.getLogger(__name__)

def run(args, game):
    """Main game loop"""
    # Setup variables used in player/world
    Game.record_loop_time()
    if Game.debug:
        # Does this get included during executable generation?
        import cave_debug

    a_serializer = Serializer(args.selected_path)
    settings_obj = a_serializer.load_settings()
    if settings_obj.get('seed') is not None:
        seed = settings_obj['seed']
    else:
        seed = args.seed
    world = World(seed)
    world.a_serializer = a_serializer
    if settings_obj.get('turn'):
        world.turn = settings_obj['turn']
    # Get save information / Generate initial objects
    Game.process()
    world.load_surrounding_blocks()
    #world.process()

    if settings_obj.get('player_index') is not None:
        player = world.blocks[(Game.idx_cur, Game.idy_cur)].objects[settings_obj['player_index']]
        player.register_actions()
    else:
        player = Player()
        Game.process()
        start_block = world.get(Game.idx_cur, Game.idy_cur)
        start_block.objects.append(player)
        start_block.reposition_object(player)
        player.update_draw_location(start_block)
        # Process to initalize object behavior
        world.process()
        # Remove cascade of loaded blocks due to 
        # object generation moving over borders
        world.cull_old_blocks(ignore_load=True)
    Game.process()
    # Draw first frame before player moves
    world.draw()

    # Get out of loop setting
    world.slow_load = True

    # Messages for out of game menu
    return_message = {}
    return_message['save'] = True
    return_message['dead'] = False
    return_message['quit'] = False

    # Counter for loop time
    # FPS
    elapsed = 0
    # Draw time
    spent_time = 0

    skipped_loads = 0
    skipped_culls = 0 

    debug_info = None

    key = libtcod.Key()
    libmouse = libtcod.Mouse()
    mouse = mouse_handler.Mouse(libmouse)
    libtcod.mouse_show_cursor(False)

    status_bar = status_handler.StatusBar()
    while True:
        Game.record_loop_time()
        if libtcod.console_is_window_closed():
            return_message['quit'] = True
            break
        # Order is important since world modifies current view
        # And game updates the relevant view variables
        player.move(world)
        if player.is_dead:
            return_message['dead'] = True
            return_message['save'] = False
            break
        # TODO, allow FPS separate from movement(multi-turn movement)
        if player.moved:
            world.process()
            world.turn += 1
            Game.process()
            libtcod.console_clear(Game.game_con)
            world.draw()
        # Load blocks during draw even if player is not doing anything
        libtcod.console_clear(Game.sidebar_con)
        libtcod.console_clear(Game.mouse_con)
        libtcod.console_clear(status_bar.con)
        if not Game.past_loop_time() or skipped_culls > 193:
            world.cull_old_blocks()
            skipped_culls = 0
        else:
            skipped_culls += 1
            log.info("skip cull")
        if not Game.past_loop_time() or skipped_loads > 547:
            world.load_surrounding_blocks()
            skipped_loads = 0
        else:
            log.info("load timeout")
            skipped_loads += 1

        status_bar.run(player, world, mouse)
        #libtcod.console_print(Game.status_con, 0, 0, "turn %s" % world.turn)
        #    libtcod.console_print(Game.status_con, 10, 0, "kills %s" % player.kills)
        if Game.debug:
            spent_time = (time.time() - Game.loop_start) * .1 + spent_time * .9
            debug_print(locals())
        #log.info("mouse (x/y) %s,%s", mouse.cx, mouse.cy)
        mouse.conditional_print()
        libtcod.console_blit(Game.game_con, x=0, y=0, w=Game.game_width, h=Game.game_height, dst=0, xdst=0, ydst=0)
        status_bar.draw()
        if not debug_info:
            libtcod.console_blit(Game.sidebar_con, x=0, y=0, w=0, h=0, dst=0, xdst=Game.game_width, ydst=0)
        libtcod.console_blit(Game.debug_con, x=0, y=0, w=0, h=0, dst=0, xdst=0, ydst=0, ffade=1, bfade=0)
        libtcod.console_blit(Game.mouse_con, x=0, y=0, w=0, h=0, dst=0, xdst=0, ydst=0, ffade=.75, bfade=.0)
        #for window in windows:
        #    window.draw()
        libtcod.console_flush()
        libtcod.console_clear(Game.debug_con)
        # ----- keyboard input -----
        status_bar.is_mode_set = False
        while True:
            libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse.mouse)
            #key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED)
            status_bar.get_input(key, mouse)
            if key.vk == libtcod.KEY_NONE:
                break
            #print("pressed {}".format(key.pressed))
            #print("char {}".format((chr(key.c))))
            #print("vk {}".format(key.vk))
            if Game.debug:
                debug_info = context_menu.debug_menu(key, debug_info, world)
                if key.pressed and key.lctrl and key.c == ord('f'):
                    if Game.action_interval:
                        Game.action_interval = 0
                        Game.move_per_sec = 0
                        libtcod.sys_set_fps(0)
                        log.info("Fast")
                    else:
                        log.info("Normal")
                        Game.action_interval = Game.default_action_interval
                        libtcod.sys_set_fps(Game.default_fps)
                        Game.move_per_sec = 3/4 * Game.default_action_interval
                        Game.action_interval = Game.default_action_interval
            player.process_input(key)
            game.get_game_input(key)
        mouse.update_coords()

        elapsed = (1/(time.time() - Game.loop_start)) * .1 + elapsed * .9

    if return_message['save']:
        world.save_active_blocks()
        logging.debug("saving seed {} at world turn {}".format(world.rand_seed, world.turn))
        world.a_serializer.save_settings(player, world)
    elif return_message['dead']:
        world.a_serializer.delete_save()
        # Reset movement keys -- bad idea to use static list
        # Register into list instance
        # TODO fix
        actions.PlayerAction.current_actions = []

    return return_message

def debug_print(args):
    """Pass locals of main loop to print debug information"""
    exec("") # Avoid locals optimization
    locals().update(args)
    libtcod.console_print(Game.debug_con, 1, 1, "FPS: %s" % str(int(elapsed)))
    libtcod.console_print(Game.debug_con, 1, 2, "blocks: %d" % len(world.blocks))
    libtcod.console_print(Game.debug_con, 1, 3, "block: (%d,%d)" % (game.idx_cur, game.idy_cur))
    libtcod.console_print(Game.debug_con, 1, 4, "view: (%dx%d)" % (game.view_x, game.view_y))
    libtcod.console_print(Game.debug_con, 1, 5, "player: (%dx%d)" % (player.x, player.y))
    libtcod.console_print(Game.debug_con, 1, 6, "process/draw time: ({0:.4f})".format(spent_time))
    num_objects = sum([len(block.objects) for block in world.blocks.values()])
    libtcod.console_print(Game.debug_con, 1, 7, "objects: {}".format(num_objects))

def main():
    """Main menu"""
    args = parse_args()
    setup_logger(args.verbose)
    log.debug("---New Game---")

    menu = Menu()
    game = Game()
    done = False
    is_dead = False
    if args.skip:
        menu.enter_game = True

    while not done:
        if not args.skip or is_dead:
            menu.enter_menu()
            if menu.quit:
                done = True
            is_dead = False
        if menu.enter_game or args.selected_path:
            if menu.selected_path:
                args.selected_path = menu.selected_path
            return_message = run(args, game)
            args.selected_path = None
            menu.selected_path = None
            done = return_message['quit']
            is_dead = return_message['dead']
        if is_dead:
            menu.game_over()
        # Sleep to stop crashing if all above if statements are false. Shouldn't
        #   happen though
        time.sleep(.1)

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', help="set world seed", default=None)
    parser.add_argument('--selected-path', help="select data folder(ignore seed)", default=None)
    parser.add_argument('--skip', help="skip main menu to new game", action="store_true")
    parser.add_argument('-v', dest='verbose', help='debug output log', action="store_true")
    args = parser.parse_args()
    return args

def setup_logger(verbose=False):
    """Setup logging -
        Only output INFO and higher to console
        Output everything to gamelog.txt
        TODO: Have an actual game log with game events
              and a separate log for debugging"""
    if verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    log.setLevel(logging.DEBUG)
    my_format = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s| %(message)s")
    #logging.basicConfig()
    fh = logging.FileHandler("gamelog.txt")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(my_format)
    log.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(console_level)
    ch.setFormatter(my_format)
    log.addHandler(ch)

if __name__ == "__main__":
    main()
