"""Container for Object and it's special subclass Player"""
import pygame
from pygame.locals import *

from game import Game

class Object:
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
        super().__init__(Game.center_x % Game.map_size, Game.center_y % Game.map_size, '@')
        self.step_modifier = 1
        self.fg = pygame.Color(139, 0, 0)
        self.bg = None

    def process_input(self, event):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.move_down = False
                self.move_up = True
            if event.key == K_DOWN:
                self.move_up = False
                self.move_down = True
            if event.key == K_LEFT:
                self.move_right = False
                self.move_left = True
            if event.key == K_RIGHT:
                self.move_left = False
                self.move_right = True
        elif event.type == KEYUP:
            if event.key == K_UP:
                self.move_up = False
            if event.key == K_DOWN:
                self.move_down = False
            if event.key == K_LEFT:
                self.move_left = False
            if event.key == K_RIGHT:
                self.move_right = False

    def move(self, cur_block):
        """ Player movement:
            NOTE: modifies view of game """
        if Game.fast:
            self.step_modifier = 100
        else:
            self.step_modifier = 1

        step = 1 * self.step_modifier

        for _ in range(step):
            if self.move_up and (not cur_block.is_obstacle(self.x, self.y-1) or not Game.collidable):
                self.y -= 1
                Game.center_y -= 1
            if self.move_down and (not cur_block.is_obstacle(self.x, self.y+1) or not Game.collidable):
                self.y += 1
                Game.center_y += 1
            if self.move_left and (not cur_block.is_obstacle(self.x -1, self.y) or not Game.collidable):
                self.x -= 1
                Game.center_x -= 1
            if self.move_right and (not cur_block.is_obstacle(self.x +1, self.y) or not Game.collidable):
                self.x += 1
                Game.center_x += 1
