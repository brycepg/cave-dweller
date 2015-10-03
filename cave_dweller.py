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

import pygame
from pygame.locals import *
import pygcurse

from game import Game
from world import World
from objects import Player

def main(seed=None):
    """Main game loop"""
    game = Game()

    # Setup variables used in player/world
    Game.record_loop_time()
    Game.process()

    #box_width = 40
    #text = "Loading ..."
    #box = pygcurse.PygcurseTextbox(Game.win, (Game.screen_width//2 - box_width//2, Game.screen_width//2 - box_width//2, box_width, box_width//2), text = text , fgcolor='white' , marginleft=box_width//2 - len(text)//2 - 1, margintop=box_width//4-2)
    #box.update()
    #Game.win.update()
    #pygame.display.update()
    #pygame.display.set_mode((0,0), RESIZABLE)

    player = Player()
    world = World(seed)
    start_block = world.get(game.idx_cur, game.idy_cur)
    start_block.objects.append(player)
    start_block.reposition_objects()

    elapsed = 0
    while True:
        Game.record_loop_time()
        for event in pygame.event.get():
            #print(event)
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            player.process_input(event)
            game.get_game_input(event)
        # Order is important since world modifies current view 
        # And game updates the relevant view variables
        world.process()
        Game.process()

        # ------- Draw -------
        world.draw()
        if Game.debug:
            Game.win.putchars("FPS: {}".format(str(int(elapsed))), 0, 0, 'red')
            Game.win.putchars("blocks: {}".format(len(world.blocks)), 0, 1, 'red')
            Game.win.putchars("block: ({},{})".format(game.idx_cur, game.idy_cur), 0, 2, 'red')
            Game.win.putchars("center: ({}x{})".format(game.center_x, game.center_y), 0, 3, 'red')
            Game.win.putchars("player: ({}x{})".format(player.x, player.y), 0, 4, 'red')
            spent_time = time.time() - Game.loop_start
            Game.win.putchars("spent_time: ({})".format(spent_time), 0, 5, 'red')
        Game.win.update()
        pygame.display.update()

        # Sleep
        elapsed = 1/(time.time() - Game.loop_start)
        game.game_clock.tick(Game.fps)

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
