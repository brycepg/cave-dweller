"""Container for Game class"""
import time
import os
import logging

import libtcodpy as libtcod


class Game(object):
    """Manages static constants,
    mutable viewing state,
    and input to change game-wide settings(for debugging)
    """
    fullscreen = False

    map_size = 96
    loaded_block_radius = 1

    font_size = 12

    screen_width = 62
    screen_height = 44

    game_width = screen_height - 1
    game_height = screen_height - 1

    status_bar_width = screen_width
    status_bar_height = screen_height - game_height

    game_con = None
    status_con = None
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

    loop_start = None
    loop_time = 1.0/fps

    font_sizes = [16, 12, 10]

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
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.font_size_index = 2
        for index, size in enumerate(Game.font_sizes):
            res_x, res_y = libtcod.sys_get_current_resolution()
            if not (Game.screen_height * size + 100 > res_y or
                    Game.screen_width * size > res_x):
                    self.font_size_index = index
                    break
        else:
            self.font_size_index = len(Game.font_sizes) - 1

        libtcod.console_set_custom_font(os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'.format(size=type(self).font_sizes[self.font_size_index])), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(type(self).screen_width, type(self).screen_height, 'Cave Dweller', Game.fullscreen, libtcod.RENDERER_SDL)
        Game.game_con = libtcod.console_new(Game.game_width, Game.game_height)
        libtcod.console_set_default_foreground(Game.game_con, libtcod.white)
        Game.status_con = libtcod.console_new(Game.status_bar_width, Game.status_bar_height)
        Game.sidebar_con = libtcod.console_new(Game.screen_width - Game.game_width, Game.screen_height)
        Game.debug_con = libtcod.console_new(Game.game_width, Game.game_height)
        Game.mouse_con = libtcod.console_new(Game.screen_width, Game.screen_height)

        libtcod.mouse_show_cursor(True)
        libtcod.sys_set_fps(type(self).fps)
        #libtcod.console_set_keyboard_repeat(1000, 100)
        libtcod.console_disable_keyboard_repeat()


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
        cls.min_x = cls.center_x - cls.game_width//2
        cls.max_x = cls.center_x + cls.game_width//2
        cls.min_y = cls.center_y - cls.game_height//2
        cls.max_y = cls.center_y + cls.game_height//2

        cls.idx_cur = cls.center_x // cls.map_size
        cls.idy_cur = cls.center_y // cls.map_size

    def get_game_input(self, key):
        if key.pressed:
            if key.lctrl and key.rctrl and key.c == ord('d'):
                Game.debug = False if Game.debug else True
            if key.vk == libtcod.KEY_F11:
                Game.fullscreen = False if Game.fullscreen else True
                libtcod.console_init_root(type(self).screen_width, type(self).screen_height, 'Cave Dweller', Game.fullscreen, libtcod.RENDERER_SDL)
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

                if key.shift and mod and key.c == ord('d'):
                    import pdb; pdb.set_trace()

                font_changed = False
                if mod and key.c == ord('-') and self.font_size_index < len(type(self).font_sizes) - 1:
                        self.font_size_index += 1
                        font_changed = True
                if mod and key.c == ord('=') and self.font_size_index > 0:
                        self.font_size_index -= 1
                        font_changed = True
                if font_changed:
                    print('set font')
                    font_path = os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'.format(size=type(self).font_sizes[self.font_size_index]))
                    print(font_path)
                    libtcod.console_delete(0)
                    libtcod.console_set_custom_font(
                            font_path, 
                            libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
                    libtcod.console_init_root(type(self).screen_width, type(self).screen_height, 'Cave Dweller', Game.fullscreen, libtcod.RENDERER_SDL)
                    font_changed = False
 
