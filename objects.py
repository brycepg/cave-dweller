"""Container for Object and it's special subclass Player"""

import libtcodpy as libtcod

from game import Game

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

    def move(self, cur_block):
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
        self.fg = libtcod.red
        self.bg = None

        self.move_down = None
        self.move_up = None
        self.move_left = None
        self.move_right = None

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
        else:
             if key.vk == libtcod.KEY_UP:
                 self.move_up = False
             if key.vk == libtcod.KEY_DOWN:
                 self.move_down = False
             if key.vk == libtcod.KEY_LEFT:
                 self.move_left = False
             if key.vk == libtcod.KEY_RIGHT:
                 self.move_right = False

    def move(self, cur_block):
        """ Player movement:
            NOTE: modifies view of game """
        if Game.fast:
            self.step_modifier = 10
        else:
            self.step_modifier = 1

        get_tile = cur_block.get_tile
        step = 1 * self.step_modifier

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

