#!/usr/bin/env python2
""" Call this file to start the game
Stores initalization of game, main game loop
And command-line argument processing
"""

__author__ = "Bryce Guinta"
__contact__ = "azrathud@gmail.com"
__version__ = "0.0.2"

import argparse
import sys
import time
import os
import logging

import libtcodpy as libtcod 

import menu
from game import Game
from world import World
from world import GetOutOfLoop
from objects import Player
from menu import Menu

def main(args, game):
    """Main game loop"""
    # Setup variables used in player/world
    Game.record_loop_time()

    world = World(args.seed)
    settings_obj = world.a_serializer.load_settings(world)
    try:
        Game.center_x = settings_obj['center_x']
        Game.center_y = settings_obj['center_y']
    except KeyError:
        logging.debug("center x/y not available")
    Game.process()
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
    world.slow_load = True

    elapsed = 0
    spent_time = 0

    #libtcod.console_set_default_background(0, libtcod.white)
    #libtcod.console_set_color_control(libtcod.COLCTRL_1,libtcod.red,libtcod.black)

    while not libtcod.console_is_window_closed():
        Game.record_loop_time()
        # Order is important since world modifies current view
        # And game updates the relevant view variables
        player.move()
        if player.moved:
            world.process()
            Game.process()

            # ------- Draw -------
            world.draw()
        libtcod.console_print(Game.status_con, 0, 0, "turn %s" % world.turn)
        if player.kills > 0:
            libtcod.console_print(Game.status_con, 10, 0, "kills %s" % player.kills)
        if Game.debug:
            spent_time = (time.time() - Game.loop_start) * .1 + spent_time * .9
            debug_print(locals())
        libtcod.console_blit(Game.game_con, 0, 0, Game.game_width, Game.game_height, 0, 0, 0)
        libtcod.console_blit(Game.status_con, 0, 0, 0, 0, 0, 0, Game.game_height)
        libtcod.console_flush()
        # ----- keyboard input -----
        while True:
            key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED)
            if key.vk == libtcod.KEY_NONE:
                break
            #print(event)
            #if event.type == QUIT:
            #    pygame.quit()
            #    sys.exit()
            player.process_input(key)
            game.get_game_input(key)
        # Sleep
        elapsed = (1/(time.time() - Game.loop_start)) * .1 + elapsed * .9
    world.save_active_blocks()
    logging.info("world turn {}".format(world.turn))
    world.a_serializer.save_settings(player)

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

def parse_main():
    """Parse arguments before calling main"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', help="world seed", default=None)
    parser.add_argument('--skip', help="skip main menu to new game", action="store_true")
    args = parser.parse_args()

    menu = Menu()
    game = Game()
    if not args.skip:
        menu.enter_menu()
    if menu.enter_game or args.skip:
        main(args, game)

def setup_logger():
    log = logging.getLogger()
    log.setLevel(logging.DEBUG)
    my_format = logging.Formatter("%(asctime)s:%(name)s:%(levelname)s| %(message)s")
    #logging.basicConfig()
    fh = logging.FileHandler("gamelog.txt")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(my_format)
    log.addHandler(fh)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(my_format)
    log.addHandler(ch)

if __name__ == "__main__":
    setup_logger()
    log = logging.getLogger(__name__)
    log.debug("---New Game---")
    parse_main()
