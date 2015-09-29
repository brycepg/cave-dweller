"""Container for Game class"""
import time
import pygame
import pygcurse

class Game:
    """Manages static constants and
    mutable viewing state"""
    map_size = 96

    screen_width = 64
    screen_height = 54

    debug = True
    fast = False
    fps = 40

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


