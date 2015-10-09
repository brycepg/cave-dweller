import random

import libtcodpy as libtcod

from game import Game

class PlayerAction(object):
    current_actions = []
    state_keys = []

    def __init__(self):
        PlayerAction.current_actions.append(self)
        self.var = False

    def get_input(self, key):
        pass

    def process(self, player, cur_block):
        pass

class PlayerMoveAction(PlayerAction):
    def __init__(self, state_key = None):
        """
        """
        super(PlayerMoveAction, self).__init__()
        self.state_key = state_key
        #if state_key is not None:
        #    type(self).state_keys.append(state_key)
        self.dir_dict = {'up': False, 'down': False, 'left': False, 'right': False}

    def get_input(self, key):
        if key.pressed:
            if key.c == self.state_key:
                self.var = True
            if self.var or self.state_key is None:
                if key.vk == libtcod.KEY_UP:
                    self.dir_dict['up'] = True
                    self.dir_dict['down'] = False
                if key.vk == libtcod.KEY_DOWN:
                    self.dir_dict['up'] = False
                    self.dir_dict['down'] = True
                if key.vk == libtcod.KEY_LEFT:
                    self.dir_dict['left'] = True
                    self.dir_dict['right'] = False
                if key.vk == libtcod.KEY_RIGHT:
                    self.dir_dict['left'] = False
                    self.dir_dict['right'] = True
        else:
            if key.c == self.state_key:
                self.var = False
            if key.vk == libtcod.KEY_UP:
                self.dir_dict['up'] = False
            if key.vk == libtcod.KEY_DOWN:
                self.dir_dict['down'] = False
            if key.vk == libtcod.KEY_LEFT:
                self.dir_dict['left'] = False
            if key.vk == libtcod.KEY_RIGHT:
                self.dir_dict['right'] = False

    def process(self, player, cur_block):
        if self.state_key is None or self.var:
            self.dir('up', (player.x, player.y-1), cur_block, player)
            self.dir('down', (player.x, player.y+1), cur_block, player)
            self.dir('left', (player.x-1, player.y), cur_block, player)
            self.dir('right', (player.x+1, player.y), cur_block, player)

    def dir(self, direction, coordinates, cur_block, player):
        pass

class Build(PlayerMoveAction):
    def __init__(self):
        super(type(self), self).__init__(state_key=ord('b'))

    def dir(self, direction, coordinates, cur_block, player=None):
        """If tile is buildable, then get it's 'build' tile"""
        tile = cur_block.get_tile(*coordinates)
        if self.dir_dict[direction] and tile.buildable:
            tile_choices = tile.attributes['build']
            new_tile = random.choice(tile_choices)
            cur_block.set_tile(coordinates[0], coordinates[1], new_tile)

class Dig(PlayerMoveAction):
    def __init__(self):
        super(type(self), self).__init__(state_key=ord('d'))

    def dir(self, direction, coordinates, cur_block, player=None):
        """If tile is diggable, then get it's 'dig' tile"""
        tile = cur_block.get_tile(*coordinates)
        if self.dir_dict[direction] and tile.diggable:
            tile_choices = tile.attributes['dig']
            new_tile = random.choice(tile_choices)
            cur_block.set_tile(coordinates[0], coordinates[1], new_tile)

class Move(PlayerMoveAction):
    def __init__(self):
        super(type(self), self).__init__(state_key=None)

    def dir(self, direction, coordinates, cur_block, player):
        """Move player if tile desired is not collidable or if collision is turned off"""
        tile = cur_block.get_tile(*coordinates)
        if self.dir_dict[direction] and not tile.is_obstacle or not Game.collidable:
            player.x, player.y = coordinates
