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
from game import Game
from world import World
from world import GetOutOfLoop
from objects import Player
from menu import Menu
import actions

log = logging.getLogger(__name__)

def run(args, game):
    """Main game loop"""
    # Setup variables used in player/world
    Game.record_loop_time()
    if Game.debug:
        # Does this get included during executable generation?
        import cave_debug

    world = World(args.seed)
    settings_obj = world.a_serializer.load_settings(world)
    # Get save information / Generate initial objects
    try:
        Game.center_x = settings_obj['center_x']
        Game.center_y = settings_obj['center_y']
    except KeyError:
        # No save
        pass
        #logging.debug("center x/y not available")
    Game.process()
    world.load_surrounding_blocks()
    world.process()

    if settings_obj['player']:
        player = None
        try:
            for block in world.blocks.values():
                for a_object in block.objects:
                    if isinstance(a_object, Player):
                        player = a_object
                        raise GetOutOfLoop
            else:
                logging.error("Player not found")
        except GetOutOfLoop:
            pass
        player.world = world
        player.register_actions()
    else:
        player = Player(world)
        Game.process()
        start_block = world.get(Game.idx_cur, Game.idy_cur)
        start_block.objects.append(player)
        start_block.reposition_object(player)
    world.process()
    Game.process()
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

    status_bar = collections.OrderedDict()
    while True:
        Game.record_loop_time()
        if libtcod.console_is_window_closed():
            return_message['quit'] = True
            break
        # Order is important since world modifies current view
        # And game updates the relevant view variables
        player.move()
        if player.is_dead:
            return_message['dead'] = True
            return_message['save'] = False
            break
        # TODO, allow FPS separate from movement(multi-turn movement)
        if player.moved:
            world.process()
            Game.process()

        if not Game.past_loop_time():
            libtcod.console_clear(Game.game_con)
            world.draw()
        else:
            log.debug("Past draw time")
        if not Game.past_loop_time():
            world.load_surrounding_blocks()
        else:
            pass
            #log.info("Past load time")
        world.cull_old_blocks()
        # Load blocks during draw even if player is not doing anything

        status_txt = get_status_txt(status_bar, player, world)
        libtcod.console_print(Game.status_con, 0, 0, status_txt)
        #libtcod.console_print(Game.status_con, 0, 0, "turn %s" % world.turn)
        #    libtcod.console_print(Game.status_con, 10, 0, "kills %s" % player.kills)
        if Game.debug:
            spent_time = (time.time() - Game.loop_start) * .1 + spent_time * .9
            debug_print(locals())
        libtcod.console_blit(Game.game_con, 0, 0, Game.game_width, Game.game_height, 0, 0, 0)
        libtcod.console_blit(Game.status_con, 0, 0, 0, 0, 0, 0, Game.game_height)
        libtcod.console_flush()
        libtcod.console_clear(Game.status_con)
        # ----- keyboard input -----
        while True:
            key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED)
            #print("char {}".format((key.c)))
            #print("vk {}".format(key.vk))
            #print("lctrl {}".format(key.lctrl))
            if key.vk == libtcod.KEY_NONE:
                break
            #print(event)
            #if event.type == QUIT:
            #    pygame.quit()
            #    sys.exit()
            player.process_input(key)
            game.get_game_input(key)
        elapsed = (1/(time.time() - Game.loop_start)) * .1 + elapsed * .9

    if return_message['save']:
        world.save_active_blocks()
        logging.debug("saving seed {} at world turn {}".format(world.rand_seed, world.turn))
        world.a_serializer.save_settings(player)
    elif return_message['dead']:
        world.a_serializer.delete_save()
        # Reset movement keys -- bad idea to use static list
        # TODO fix
        actions.PlayerAction.current_actions = []

    return return_message

def debug_print(args):
    """Pass locals of main loop to print debug information"""
    exec("") # Avoid locals optimization
    locals().update(args)
    libtcod.console_print(Game.game_con, 1, 1, "FPS: %s" % str(int(elapsed)))
    libtcod.console_print(Game.game_con, 1, 2, "blocks: %d" % len(world.blocks))
    libtcod.console_print(Game.game_con, 1, 3, "block: (%d,%d)" % (game.idx_cur, game.idy_cur))
    libtcod.console_print(Game.game_con, 1, 4, "center: (%dx%d)" % (game.center_x, game.center_y))
    libtcod.console_print(Game.game_con, 1, 5, "player: (%dx%d)" % (player.x, player.y))
    libtcod.console_print(Game.game_con, 1, 6, "process/draw time: ({0:.4f})".format(spent_time))
    num_objects = sum([len(block.objects) for block in world.blocks.values()])
    libtcod.console_print(Game.game_con, 1, 7, "objects: {}".format(num_objects))

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
        if menu.enter_game:
            if menu.selected_seed:
                args.seed = menu.selected_seed
            return_message = run(args, game)
            done = return_message['quit']
            is_dead = return_message['dead']
            menu.selected_seed = None
        if is_dead:
            menu.game_over()
        # Sleep to stop crashing if all above if statements are false. Shouldn't 
        #   happen though
        time.sleep(.1)

def parse_args():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', help="set world seed", default=None)
    parser.add_argument('--skip', help="skip main menu to new game", action="store_true")
    parser.add_argument('-v', dest='verbose', help='debug output log', action="store_true")
    args = parser.parse_args()
    return args

def get_status_txt(status_bar, player, world):
    """Generate status bar text for game"""
    # Dynamic status list
    status_bar['turn'] = ['Turn ', str(world.turn)]
    if player.kills > 0:
        status_bar['kills'] = [' Kills ', str(player.kills)]
    if Game.debug:
        status_bar[' '] = [' ']
        status_bar['debug'] = ['Debug']
    else:
        status_bar[' '] = []
        status_bar['debug'] = []

    status_list = []
    for a_list in status_bar.values():
        status_list.append(''.join(a_list))
    status_txt = ''.join(status_list)
    return status_txt

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
    log = logging.getLogger()
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
