"""Container for Object and it's special subclass Player"""

import random 
import time

import libtcodpy as libtcod

from game import Game
from tiles import Id
import actions

class Object(object):
    """ Non-terrain entities"""
    def __init__(self, x=None, y=None, char=None):
        self.x = x
        self.y = y
        self.char = char

        self.bg = None
        self.fg = None

        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        self.new_block = False

    def process(self, cur_block):
        """Configuration that changes object state"""
        pass

    def out_of_bounds(self):
        """Check if object is out of bounds of local
        block-coordinate system"""
        if (self.x < 0 or
                self.x >= Game.map_size or
                self.y < 0 or
                self.y >= Game.map_size):
            return True
        else:
            return False

class Player(Object):
    """Player-object
       Acts as an object but also manages the viewable center"""
    def __init__(self):
        super(type(self), self).__init__(Game.center_x % Game.map_size, Game.center_y % Game.map_size, '@')
        self.step_modifier = 1
        self.fg = libtcod.lightest_gray
        self.bg = None

        self.last_move_time = 0
        self.last_action_time = 0

        self.move_down = None
        self.move_up = None
        self.move_left = None
        self.move_right = None

        self.dig = False
        self.dig_up = False
        self.dig_down = False
        self.dig_left = False
        self.dig_right = False

        self.build = False
        self.build_up = False
        self.build_down = False
        self.build_left = False
        self.build_right = False

        self.new_turn = False

        # Count frames
        self.last_turn = 0

        actions.Build()
        actions.Dig()
        # Order is imporant -- move last since it doesn't require a state key
        actions.Move()

    def process_input(self, key):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        for action in actions.PlayerAction.current_actions:
            action.get_input(key)

    def process(self, cur_block):
        """ Player movement:
            NOTE: modifies view of game """

        # Strictly one move per turn
        if self.last_turn == cur_block.world.turn:
            return
            
        if Game.fast:
            self.step_modifier = 10
        else:
            self.step_modifier = 1

        if (time.time() - self.last_action_time) < Game.action_interval:
            return
        self.last_action_time = time.time()

        for action in actions.PlayerAction.current_actions:
            action.process(self, cur_block)
            if action.var:
                break

        Game.center_x = int(self.x + Game.map_size * cur_block.idx)
        Game.center_y = int(self.y + Game.map_size * cur_block.idy)

        self.last_turn = cur_block.world.turn
