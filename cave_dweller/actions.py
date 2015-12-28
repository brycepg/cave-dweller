"""Implement player actions"""
import random
import time
import traceback

import libtcodpy as libtcod

from game import Game

class PlayerAction(object):
    """Virtual class"""
    current_actions = []
    turn_delta = 0

    def __init__(self):
        PlayerAction.current_actions.append(self)
        self.var = False
        self.done = False

    @classmethod
    def register(cls, subclass):
        """Register subclass into list to be later processed by player"""
        cls.current_actions.append(subclass())

    def get_input(self, key):
        """Separate input from action"""
        pass

    def process(self, player, cur_block):
        """Separate action from input"""
        pass

class PlayerMoveAction(PlayerAction):
    """Movements with states and/or that are directional in relation to the player"""
    def __init__(self, state_key=None):
        """
        Action controlled by optional state-key followed by arrow keys
        Assummed to be mutually exclusive
        """
        super(PlayerMoveAction, self).__init__()
        self.state_key = state_key
        self.dir_dict = {'up': False, 'down': False, 'left': False, 'right': False}
        self.key = None

    def get_input(self, key):
        """
        var - state key is pressed -
        dir_dict - arrow key movement state
        """
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
        self.key = key

    def process(self, player, cur_block):
        self.done = False
        if self.state_key is None or self.var:
            cur_block = self.dir('up', (player.x, player.y-1), cur_block, player)
            if self.done:
                return
            cur_block = self.dir('down', (player.x, player.y+1), cur_block, player)
            if self.done:
                return
            cur_block = self.dir('left', (player.x-1, player.y), cur_block, player)
            if self.done:
                return
            cur_block = self.dir('right', (player.x+1, player.y), cur_block, player)
            if self.done:
                return

    def dir(self, direction, coordinates, cur_block, player):
        pass

class Build(PlayerMoveAction):
    def __init__(self):
        super(type(self), self).__init__(state_key=ord('b'))

    def dir(self, direction, coordinates, cur_block, player=None):
        """If tile is buildable, then get it's 'build' tile"""
        tile = cur_block.get_tile(*coordinates)
        if self.dir_dict[direction] and tile.buildable and not cur_block.get_entity(*coordinates):
            tile_choices = tile.attributes['build']
            new_tile = random.choice(tile_choices)
            cur_block.set_tile(coordinates[0], coordinates[1], new_tile)
            player.moved = True
            self.done = True
        return cur_block

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
            player.moved = True
            self.done = True
        return cur_block

class Move(PlayerMoveAction):
    def __init__(self):
        super(type(self), self).__init__(state_key=None)
        self.last_move_time = 0

    def process(self, player, cur_block):
        # Prevent key-repeat - Limit movement per second
        if (time.time() - self.last_move_time) < Game.move_per_sec:
            return
        self.last_move_time = time.time()

        super(type(self), self).process(player, cur_block)

    def dir(self, direction, coordinates, cur_block, player):
        """Move player if tile desired is not collidable or if collision is turned off"""
        tile = cur_block.get_tile(*coordinates)
        if self.dir_dict[direction]:
            obj = cur_block.get_entity(*coordinates)
            if not (obj and obj.is_obstacle) and not tile.is_obstacle or not Game.collidable:
                cur_block = cur_block.move_entity(player, *coordinates)
                player.moved = True
        return cur_block

class Attack(PlayerMoveAction):
    def __init__(self):
        super(type(self), self).__init__(state_key=ord('k'))

    def dir(self, direction, coordinates, cur_block, player):
        if self.dir_dict[direction]:
            obj = cur_block.get_entity(*coordinates)
            if obj and not obj.is_dead:
                obj.kill()
                player.moved = True
                player.kills += 1
        return cur_block

class Wait(PlayerAction):
    """Wait(.), skip a turn
       Wait fast(>), keep skipping turns until escape is pressed.
       (probably should only enable for debug)"""

    def __init__(self):
        super(type(self), self).__init__()
        self.wait = False
        self.wait_fast = False

    def get_input(self, key):
        if key.c == ord('>'):
            self.wait_fast = True
        if key.c == ord('.'):
            self.wait = True
        else:
            self.wait = False

        if key.vk == libtcod.KEY_ESCAPE:
            self.wait_fast = False


    def process(self, player, cur_block):
        if self.wait:
            self.wait = False
            player.moved = True
        if self.wait_fast:
            # Action interval is used in player to limit actions per second
            #   (to stop key repeats)
            # No limit to fps too
            Game.action_interval = 0
            libtcod.sys_set_fps(0)
            self.wait = True
            player.moved = True
        if not self.wait_fast:
            Game.action_interval = Game.default_action_interval
            libtcod.sys_set_fps(Game.fps)
