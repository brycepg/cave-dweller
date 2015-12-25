"""Container for Game class"""
import time
import os
import logging

import libtcodpy as libtcod

from font_handler import FontHandler

class Game(object):
    """Manages static constants,
    mutable viewing state,
    and input to change game-wide settings(for debugging)
    """
    fullscreen = False

    map_size = 96
    loaded_block_radius = 1

    screen_width = 62
    screen_height = 44

    game_width = screen_height - 1
    game_height = screen_height - 1

    game_con = None
    mouse_con = None
    debug_con = None
    sidebar_con = None

    debug = True
    collidable = True
    reposition_objects = False

    default_fps = 30
    fps = default_fps
    default_action_interval = 1.0/20
    move_per_sec = 3/4 * default_action_interval
    action_interval = default_action_interval

    # Drawable window
    win = None

    # Center coordinates of drawable area
    view_x = 0
    view_y = 0

    # Bound coordinates of drawable area
    min_x = None
    min_y = None
    max_x = None
    max_y = None

    # Current view block coordinates
    idx_cur = None
    idy_cur = None

    loop_start = None
    loop_time = 1.0/fps

    @classmethod
    def in_drawable_coordinates(cls, abs_x, abs_y):
        """Check if absolute coordinate is in drawable area"""
        if(cls.min_x <= abs_x <= cls.max_x
           and cls.min_y <= abs_y <= cls.max_y):
            return True
        else:
            return False


    def __init__(self):
        logging.info("game init")
        # Tries to center the cosnole during init
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.font_handler = FontHandler()
        self.init_consoles()

    def init_consoles(self):
        self.bring_up_root()
        Game.game_con = libtcod.console_new(Game.game_width, Game.game_height)
        Game.sidebar_con = libtcod.console_new(Game.screen_width - Game.game_width,
                                               Game.screen_height)
        Game.debug_con = libtcod.console_new(Game.game_width, Game.game_height)
        Game.mouse_con = libtcod.console_new(Game.screen_width, Game.screen_height)

    def bring_up_root(self):
        """Call relevant settings and then bringing up the root console."""
        self.font_handler.set_font()
        libtcod.console_disable_keyboard_repeat()
        libtcod.sys_set_fps(type(self).fps)
        libtcod.mouse_show_cursor(False)
        libtcod.console_init_root(Game.screen_width, Game.screen_height,
                                  'Cave Dweller',
                                  Game.fullscreen, libtcod.RENDERER_SDL)


    @classmethod
    def record_loop_time(cls):
        """Call at the beginning of every loop to allow for time recording"""
        cls.loop_start = time.time()

    @classmethod
    def past_loop_time(cls):
        """Check if game loop needs to exit to keep up framerate"""
        if (time.time() - cls.loop_start) > cls.loop_time:
            return True
        else:
            return False

    @classmethod
    def process(cls):
        """Update game viewable current location variables"""
        cls.min_x = cls.view_x
        cls.max_x = cls.view_x + cls.game_width
        cls.min_y = cls.view_y
        cls.max_y = cls.view_y + cls.game_height

        cls.idx_cur = (cls.view_x + Game.game_width) // cls.map_size 
        cls.idy_cur = (cls.view_y + Game.game_height) // cls.map_size

    def get_game_input(self, key):
        if key.pressed:
            if key.lctrl and key.rctrl and key.c == ord('d'):
                Game.debug = False if Game.debug else True
            if key.vk == libtcod.KEY_F11:
                Game.fullscreen = False if Game.fullscreen else True
                libtcod.console_delete(0)
                self.font_handler.set_font()
                self.bring_up_root()
        if Game.debug:
            if key.pressed:
                mod = key.lctrl
                if mod and key.c == ord('c'):
                    Game.collidable = False if Game.collidable else True
                    print('toggle collision: {}'.format(Game.collidable))
                    if Game.collidable:
                        Game.reposition_objects = True
                # TODO get working again
                if mod and key.c == ord('-') and Game.fps > 0:
                    Game.fps -= 1
                    print("fps: %d" % Game.fps)
                    libtcod.sys_set_fps(type(self).fps)
                if mod and key.c == ord('='):
                    Game.fps += 1
                    print("fps: %d" % Game.fps)
                    libtcod.sys_set_fps(type(self).fps)
                if mod and key.c == ord('0'):
                    Game.fps = 0
                    print("fps unlimited")
                    libtcod.sys_set_fps(type(self).fps)
                if mod and key.vk == libtcod.KEY_1:
                    Game.fps = Game.default_fps
                    print("fps default: %d" % Game.default_fps)
                    libtcod.sys_set_fps(type(self).fps)
                if mod and key.vk == libtcod.KEY_2:
                    Game.fps += Game.default_fps
                    print("fps: %d" % Game.fps)
                    libtcod.sys_set_fps(type(self).fps)

                CTRL_R_BRACKET = 29
                CTRL_L_BRACKET = 27
                if key.c == CTRL_L_BRACKET and key.lctrl and Game.loaded_block_radius > 0:
                #if key.c == ord("[") and key.lalt and Game.loaded_block_radius > 0:
                    Game.loaded_block_radius -= 1
                    print("loaded block radius: %d" % Game.loaded_block_radius)
                if key.c == CTRL_R_BRACKET and key.lctrl:
                    Game.loaded_block_radius += 1
                    print("loaded block radius: %d" % Game.loaded_block_radius)

                font_changed = False
                if mod and key.c == ord('-') and self.font_handler.decrease_font():
                        font_changed = True
                if mod and key.c == ord('=') and self.font_handler.increase_font():
                        font_changed = True
                if font_changed:
                    print('set font')
                    libtcod.console_delete(0)
                    self.bring_up_root()
 
                if key.shift and mod and key.c == ord('d'):
                    import pdb; pdb.set_trace()

