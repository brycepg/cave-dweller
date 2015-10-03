"""Container for Game class"""
import time
import os

import pygame
from pygame.locals import *
import pygcurse

class Game:
    """Manages static constants,
    mutable viewing state,
    and input to change game-wide settings(for debugging)
    """
    map_size = 96
    font_size = 18

    screen_width = 64
    screen_height = 32

    debug = True
    fast = False
    collidable = True
    show_algorithm = False
    fps = 10

    # Drawable window
    win = None

    # Center coordinates of drawable area
    center_x = 0
    center_y = 0
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Bound coordinates of drawable area
    min_x = None
    min_y = None
    max_x = None
    max_y = None

    # Current view block coordinates
    idx_cur = None
    idy_cur = None

    win = None

    loop_start = None
    loop_time = 1/fps

    @classmethod
    def in_drawable_coordinates(cls, abs_x, abs_y):
        """Check if absolute coordinate is in drawable area"""
        if(cls.min_x <= abs_x <= cls.max_x
           and cls.min_y <= abs_y <= cls.max_y):
            return True
        else:
            return False

    def __init__(self):
        # TODO
        #self.text_font = pygame.font.SysFont("monospace", 15)
        Game.win = pygcurse.PygcurseWindow(self.screen_width,
                                           self.screen_height,
                                           fullscreen=False)
        Game.win.font = pygame.font.Font(os.path.join('fonts', 'DejaVuSerif.ttf'), Game.font_size)
        #Game.win.font = pygame.font.Font(os.path.join('fonts', 'dog_vga_437.ttf'), Game.font_size)
        pygame.display.set_caption('Cave Dweller')
        Game.win.autowindowupdate = False
        Game.win.autoupdate = False


        Game.game_clock = pygame.time.Clock()

    @classmethod
    def record_loop_time(cls):
        """Call at the beginning of every loop to allow for time recording"""
        cls.loop_start = time.time()

    @classmethod
    def past_loop_time(cls):
        """Check if game loop needs to exit to keep up framerate"""
        if time.time() - cls.loop_start > cls.loop_time/2:
            return True
        else:
            return False

    @classmethod
    def process(cls):
        """Update game viewable current location variables"""
        cls.min_x = cls.center_x - cls.screen_width//2
        cls.max_x = cls.center_x + cls.screen_width//2
        cls.min_y = cls.center_y - cls.screen_height//2
        cls.max_y = cls.center_y + cls.screen_height//2

        cls.idx_cur = cls.center_x // cls.map_size
        cls.idy_cur = cls.center_y // cls.map_size

    def get_game_input(self, event):
        if event.type == KEYDOWN:
            if pygame.key.get_mods() & (KMOD_LCTRL | KMOD_RCTRL) and event.key == K_d:
                Game.debug = False if Game.debug else True
                print('toggle debug: {}'.format(Game.debug))
        if Game.debug:
            if event.type == KEYDOWN:
                mod = pygame.key.get_mods() & KMOD_LCTRL
                if mod and event.key == K_f:
                    Game.fast = False if Game.fast else True
                    print('toggle speed: {}'.format(Game.fast))
                if mod and event.key == K_c:
                    Game.collidable = False if Game.collidable else True
                    print('toggle collision: {}'.format(Game.collidable))


#                font_size_modifier = 2
#               if mod and event.key == K_EQUALS:
#                   self.screen_width -= 1
#                   self.screen_height -= 1
#                   Game.win.resize(self.screen_width, self.screen_height)
#                    Game.font_size += font_size_modifier
#                    Game.win.font = pygame.font.Font(os.path.join('fonts', 'DejaVuSerif.ttf'), Game.font_size)
#               if mod and event.key == K_MINUS:
#                   self.screen_width += 1
#                   self.screen_height += 1
#                   Game.win.resize(self.screen_width, self.screen_height)

