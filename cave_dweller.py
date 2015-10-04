#!/usr/bin/env python3
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

from game import Game
from world import World
from objects import Player

def main(seed=None):
    """Main game loop"""
    game = Game()

    # Setup variables used in player/world
    Game.record_loop_time()
    Game.process()

    player = Player()
    world = World(seed)
    start_block = world.get(game.idx_cur, game.idy_cur)
    start_block.objects.append(player)
    start_block.reposition_objects()

    elapsed = 0
    spent_time = 0

    #libtcod.console_set_default_foreground(0, libtcod.white)
    #libtcod.console_set_default_background(0, libtcod.white)
    #libtcod.console_set_color_control(libtcod.COLCTRL_1,libtcod.red,libtcod.black)

    while not libtcod.console_is_window_closed():
        Game.record_loop_time()
        # Order is important since world modifies current view 
        # And game updates the relevant view variables
        world.process()
        Game.process()

        # ------- Draw -------
        world.draw()
        if Game.debug:
            libtcod.console_print(0, 1, 1, "FPS: %s" % str(int(elapsed)))
            libtcod.console_print(0, 1, 2, "blocks: %d" % len(world.blocks))
            libtcod.console_print(0, 1, 3, "block: (%d,%d)" % (game.idx_cur, game.idy_cur))
            libtcod.console_print(0, 1, 4, "center: (%dx%d)" % (game.center_x, game.center_y))
            libtcod.console_print(0, 1, 5, "player: (%dx%d)" % (player.x, player.y))
            spent_time = (time.time() - Game.loop_start) * .1 + spent_time * .9
            libtcod.console_print(0, 1, 6, "process/draw time: ({0:.4f})".format(spent_time))
        #Game.win.update()
        #pygame.display.update()
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
        elapsed = 1/(time.time() - Game.loop_start)

def debug(my_locals):
    pass

def parse_main():
    """Parse arguments before calling main"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', help="world seed")
    args = parser.parse_args()


    if args.seed:
        main(int(args.seed))
    else:
        main()

if __name__ == "__main__":
    parse_main()
