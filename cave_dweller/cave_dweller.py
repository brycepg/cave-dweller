#!/usr/bin/env python2
""" Call this file to start the game
Stores initalization of game, main game loop
"""

__author__ = "Bryce Guinta"
__contact__ = "azrathud@gmail.com"
__version__ = "0.0.5"

import time
import logging

from .run_game import run
from .game import Game
from .menu import Menu
from .args import parse_args
from .log_setup import setup_logger

log = logging.getLogger(__name__)

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

    # TODO state machine class
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

if __name__ == "__main__":
    main()
