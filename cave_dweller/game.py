"""Container for Game class"""
import time
import os
import logging

import libtcodpy as libtcod

from font_handler import FontHandler
import tiles

from libtcodpy import _lib
from ctypes import c_float
console_blit = _lib.TCOD_console_blit
sys_check_for_event = _lib.TCOD_sys_check_for_event
ffade = c_float(1.0)
bfade = c_float(1.0)
transparent_fade = c_float(0.0)
mouse_ffade = c_float(0.75)

class Game(object):
    """Manages static constants,
    mutable viewing state,
    and input to change game-wide settings(for debugging)
    """
    fullscreen = False

    map_size = 96
    loaded_block_radius = 1

    screen_width = 96
    screen_height = 51

    sidebar_enabled = False
    game_width = screen_height - 1 if sidebar_enabled else screen_width
    game_height = screen_height - 1
    redraw_consoles = False
    redraw_sidebar = False

    @classmethod
    def set_sidebar(cls, bool_val):
        cls.sidebar_enabled = bool_val
        cls.game_width = cls.screen_height - 1 if cls.sidebar_enabled else cls.screen_width
        # SIGSEV on console delete? (Only with multiple console deletes?)
        # This function causes memory leaks! YAY
        cls.init_consoles(init_root=False)
        cls.redraw_consoles = True


    game_con = None
    mouse_con = None
    debug_con = None

    sidebar_con = None

    debug = True
    collidable = True

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


    active_consoles = []
    font_handler = None
    def __init__(self):
        if max(Game.game_width, Game.game_height) > Game.map_size:
            raise RuntimeError("Screen window is bigger than map size"
                               "(need to change draw algorithm)")
        logging.info("game init")
        # Tries to center the cosnole during init
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        Game.font_handler = FontHandler()
        Game.init_consoles()
        self.update_view()

    @classmethod
    def blit_consoles(cls, status_bar, debug_info=None):
        console_blit(Game.game_con, 0, 0,
                             Game.game_width, Game.game_height,
                             0, 0, 0, ffade, bfade)
        if status_bar:
            status_bar.draw()
        if not debug_info and Game.sidebar_enabled:
            console_blit(Game.sidebar_con, 0, 0, 0, 0,
                                 0, Game.game_width, 0, ffade, bfade)
        console_blit(Game.debug_con, 0, 0, 0, 0,
                             0, 0, 0, ffade, transparent_fade)
        console_blit(Game.mouse_con, 0, 0, 0, 0,
                             0, 0, 0, mouse_ffade, transparent_fade)

    @classmethod
    def init_consoles(cls, init_root=True):
        if init_root:
            cls.bring_up_root()
        Game.game_con = libtcod.console_new(Game.game_width, Game.game_height)
        Game.active_consoles.append(Game.game_con)

        Game.sidebar_con = libtcod.console_new(Game.screen_width - Game.game_width,
                                                Game.screen_height)
        Game.active_consoles.append(Game.sidebar_con)
        libtcod.console_set_default_background(Game.sidebar_con, libtcod.dark_gray)
        Game.debug_con = libtcod.console_new(Game.game_width, Game.game_height)
        Game.active_consoles.append(Game.debug_con)

        Game.mouse_con = libtcod.console_new(Game.screen_width, Game.screen_height)
        Game.active_consoles.append(Game.mouse_con)
        for console in Game.active_consoles:
            libtcod.console_clear(console)

    @classmethod
    def delete_consoles(cls):
        libtcod.console_flush()
        for console in Game.active_consoles:
            libtcod.console_clear(console)
            libtcod.console_delete(console)
        Game.active_consoles = []

    @classmethod
    def bring_up_root(cls):
        """Call relevant settings and then bringing up the root console."""
        cls.font_handler.set_font()
        # TODO modify libtcod to fix cursor problem with resize
        libtcod.console_disable_keyboard_repeat()
        libtcod.sys_set_fps(cls.fps)
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
    def update_view(cls):
        """Update game viewable current location variables"""
        cls.min_x = cls.view_x
        cls.max_x = cls.view_x + cls.game_width
        cls.min_y = cls.view_y
        cls.max_y = cls.view_y + cls.game_height

        cls.idx_cur = (cls.view_x + Game.game_width//2) // cls.map_size
        cls.idy_cur = (cls.view_y + Game.game_height//2) // cls.map_size

    @classmethod
    def toggle_sidebar(cls):
        cls.set_sidebar(False if cls.sidebar_enabled else True)

    def get_game_input(self, key):
        if key.pressed:
            if key.lctrl and key.rctrl and key.c == ord('d'):
                Game.debug = False if Game.debug else True
            if key.vk == libtcod.KEY_F11:
                Game.fullscreen = False if Game.fullscreen else True
                self.bring_up_root()
            if key.vk == libtcod.KEY_F5:
                Game.toggle_sidebar()
        if Game.debug:
            if key.pressed:
                mod = key.lctrl
                if mod and key.c == ord('c'):
                    Game.collidable = False if Game.collidable else True
                    print('toggle collision: {}'.format(Game.collidable))
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
                    import pdb
                    pdb.set_trace()

