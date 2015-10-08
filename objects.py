"""Container for Object and it's special subclass Player"""

import random 
import time

import libtcodpy as libtcod

from game import Game
from tiles import Id

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

        # Count frames
        self.last_turn = 0

    def process_input(self, key):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        #print("key: vk:{} c:{} pressed:{}".format(key.vk, key.c, key.pressed))
        if key.pressed:
            if key.vk == libtcod.KEY_UP:
                self.move_down = False
                self.move_up = True
            if key.vk == libtcod.KEY_DOWN:
                self.move_up = False
                self.move_down = True
            if key.vk == libtcod.KEY_LEFT:
                self.move_right = False
                self.move_left = True
            if key.vk == libtcod.KEY_RIGHT:
                self.move_left = False
                self.move_right = True
            if key.c == ord('d'):
                self.dig = True
            if key.c == ord('b'):
                self.build = True
            if self.dig:
                if key.vk == libtcod.KEY_UP:
                    self.dig_up = True
                if key.vk == libtcod.KEY_DOWN:
                    self.dig_down = True
                if key.vk == libtcod.KEY_LEFT:
                    self.dig_left = True
                if key.vk == libtcod.KEY_RIGHT:
                    self.dig_right = True
            if self.build:
                if key.vk == libtcod.KEY_UP:
                    self.build_up = True
                if key.vk == libtcod.KEY_DOWN:
                    self.build_down = True
                if key.vk == libtcod.KEY_LEFT:
                    self.build_left = True
                if key.vk == libtcod.KEY_RIGHT:
                    self.build_right = True
        else:
            if key.c == ord('d'):
                self.dig = False
            if key.c == ord('b'):
                self.build = False
            if key.vk == libtcod.KEY_UP:
                self.move_up = False
                self.dig_up = False
                self.build_up = False
            if key.vk == libtcod.KEY_DOWN:
                self.move_down = False
                self.dig_down = False
                self.build_down = False
            if key.vk == libtcod.KEY_LEFT:
                self.move_left = False
                self.dig_left = False
                self.build_left = False
            if key.vk == libtcod.KEY_RIGHT:
                self.move_right = False
                self.dig_right = False
                self.build_right = False

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


        get_tile = cur_block.get_tile
        step = 1 * self.step_modifier
        if (time.time() - self.last_action_time) < Game.action_interval:
            return
        self.last_action_time = time.time()

        if self.dig:
            up = cur_block.get_tile(self.x, self.y-1)
            down = cur_block.get_tile(self.x, self.y+1)
            left = cur_block.get_tile(self.x-1, self.y)
            right = cur_block.get_tile(self.x+1, self.y)
            if self.dig_left and left.diggable:
                tile_choices = left.attributes['dig']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x-1, self.y, new_tile)
            elif self.dig_right and right.diggable:
                tile_choices = right.attributes['dig']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x+1, self.y, new_tile)
            elif self.dig_up and up.diggable:
                tile_choices = up.attributes['dig']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x, self.y-1, new_tile)
            elif self.dig_down and down.diggable:
                tile_choices = down.attributes['dig']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x, self.y+1, new_tile)

        elif self.build:
            up = cur_block.get_tile(self.x, self.y-1)
            down = cur_block.get_tile(self.x, self.y+1)
            left = cur_block.get_tile(self.x-1, self.y)
            right = cur_block.get_tile(self.x+1, self.y)
            if self.build_left and left.buildable:
                tile_choices = left.attributes['build']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x-1, self.y, new_tile)
            elif self.build_right and right.buildable:
                tile_choices = right.attributes['build']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x+1, self.y, new_tile)
            elif self.build_up and up.buildable:
                tile_choices = up.attributes['build']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x, self.y-1, new_tile)
            elif self.build_down and down.buildable:
                tile_choices = down.attributes['build']
                new_tile = random.choice(tile_choices)
                cur_block.set_tile(self.x, self.y+1, new_tile)

        else:
            # Limit movement per second
            if (time.time() - self.last_move_time) < Game.move_per_sec:
                return
            self.last_move_time = time.time()
            for _ in range(step):
                if self.move_up and (not cur_block.get_tile(self.x, self.y-1).is_obstacle or not Game.collidable):
                    self.y -= 1
                if self.move_down and (not cur_block.get_tile(self.x, self.y+1).is_obstacle or not Game.collidable):
                    self.y += 1
                if self.move_left and (not cur_block.get_tile(self.x -1, self.y).is_obstacle or not Game.collidable):
                    self.x -= 1
                if self.move_right and (not cur_block.get_tile(self.x +1, self.y).is_obstacle or not Game.collidable):
                    self.x += 1
        Game.center_x = int(self.x + Game.map_size * cur_block.idx)
        Game.center_y = int(self.y + Game.map_size * cur_block.idy)

        self.last_turn = cur_block.world.turn
