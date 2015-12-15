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
        self.do_process = True
        self.blocking = True

        self.bg = None
        self.fg = None

        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        self.new_block = False

    def process(self, cur_block):
        """Configuration that changes object state"""
        raise NotImplementedError

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

class Cat(Object):
    """First dummy non-player entity"""
    def __init__(self, x, y):
        super(Cat, self).__init__(x, y, 'c')
        self.fg = libtcod.grey

    def process(self, cur_block):
        if not self.do_process:
            return
        x_new = self.x + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        y_new = self.y + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.move((x_new, y_new), cur_block)


    def move(self, coordinates, cur_block):
        """Move player if tile desired is not collidable or if collision is turned off"""
        tile = cur_block.get_tile(*coordinates)
        if not tile.is_obstacle and not cur_block.object_at(*coordinates):
            self.x, self.y = coordinates

class Spider(Object):
    """First dummy non-player entity"""
    def __init__(self, x, y):
        super(Spider, self).__init__(x, y, 'S')
        self.fg = libtcod.grey

    def process(self, cur_block):
        if not self.do_process:
            return
        x_new = self.x + random.choice([-1, 0, 0, 0, 1])
        y_new = self.y + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.move((x_new, y_new), cur_block)


    def move(self, coordinates, cur_block):
        """Move player if tile desired is not collidable or if collision is turned off"""
        tile = cur_block.get_tile(*coordinates)
        if not tile.is_obstacle and not cur_block.object_at(*coordinates):
            self.x, self.y = coordinates


class Player(Object):
    """Player-object
       Acts as an object but also manages the viewable center"""
    def __init__(self, world):
        super(Player, self).__init__(Game.center_x % Game.map_size,
                                     Game.center_y % Game.map_size,
                                     '@')
        self.world = world
        self.fg = libtcod.lightest_gray
        self.bg = None

        self.moved = False

        self.last_move_time = 0
        self.last_action_time = 0

        self.new_turn = False

        # Count frames
        self.last_turn = 0

        actions.Build()
        actions.Dig()
        # Order is imporant -- move last since it doesn't require a state key
        actions.Move()
        actions.Attack()

    def process_input(self, key):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        for action in actions.PlayerAction.current_actions:
            action.get_input(key)

    def move(self):
        block = self.world.get_block(Game.center_x, Game.center_y)
        self.moved = False

        #if self.last_turn == self.world.turn:
        #    return
        #self.last_turn = self.world.turn

        if (time.time() - self.last_action_time) < Game.action_interval:
            return

        for action in actions.PlayerAction.current_actions:
            action.process(self, block)
            if self.moved:
                break

        self.last_action_time = time.time()

    def process(self, cur_block):
        """ Player movement:
            NOTE: modifies view of game """
        Game.center_x = int(self.x + Game.map_size * cur_block.idx)
        Game.center_y = int(self.y + Game.map_size * cur_block.idy)

class Empty:
    def process(self, cur_block):
        pass

# Hack for generating classes
# Class | chance of generation for each entity | max number of entitites
generation_table = [
    [Cat, 100, 20],
    [Spider, 50, 5]
]

