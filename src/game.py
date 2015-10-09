"""Container for Game class"""
import time
import os

import libtcodpy as libtcod

class Game(object):
    """Manages static constants,
    mutable viewing state,
    and input to change game-wide settings(for debugging)
    """
    map_size = 96
    loaded_block_radius = 1

    font_size = 12

    screen_width = 62
    screen_height = 40

    debug = True
    fast = False
    collidable = True
    show_algorithm = False
    reposition_objects = False

    default_fps = 24
    fps = default_fps
    move_per_sec = 1.0/15
    action_interval = 1.0/20

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

    font_sizes = [10, 12, 16]

    @classmethod
    def in_drawable_coordinates(cls, abs_x, abs_y):
        """Check if absolute coordinate is in drawable area"""
        if(cls.min_x <= abs_x <= cls.max_x
           and cls.min_y <= abs_y <= cls.max_y):
            return True
        else:
            return False

    def __init__(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        self.font_size_index = 2
        libtcod.console_set_custom_font(os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'.format(size=type(self).font_sizes[self.font_size_index])), libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
        libtcod.console_init_root(type(self).screen_width, type(self).screen_height, 'Cave Dweller', libtcod.RENDERER_GLSL)

        libtcod.mouse_show_cursor(True)
        libtcod.sys_set_fps(type(self).fps)
        libtcod.console_set_keyboard_repeat(5, 100)


    @classmethod
    def record_loop_time(cls):
        """Call at the beginning of every loop to allow for time recording"""
        cls.loop_start = time.time()

    @classmethod
    def past_loop_time(cls):
        """Check if game loop needs to exit to keep up framerate"""
        if (time.time() - cls.loop_start) > cls.loop_time/2:
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

    def get_game_input(self, key):
        if key.pressed:
            if key.lctrl and key.rctrl and key.c == ord('d'):
                Game.debug = False if Game.debug else True
        if Game.debug:
            if key.pressed:
                mod = key.lctrl
                if mod and key.c == ord('f'):
                    Game.fast = False if Game.fast else True
                    print('toggle speed: {}'.format(Game.fast))
                if mod and key.c == ord('c'):
                    Game.collidable = False if Game.collidable else True
                    print('toggle collision: {}'.format(Game.collidable))
                    if Game.collidable:
                        Game.reposition_objects = True
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

                #print key.c
                CTRL_R_BRACKET = 29
                CTRL_L_BRACKET = 27
                if key.c == CTRL_L_BRACKET and Game.loaded_block_radius > 0:
                    Game.loaded_block_radius -= 1
                    print("loaded block radius: %d" % Game.loaded_block_radius)
                if key.c == CTRL_R_BRACKET:
                    Game.loaded_block_radius += 1
                    print("loaded block radius: %d" % Game.loaded_block_radius)

                if mod and key.c == ord('s'):
                    Game.show_algorithm = False if Game.show_algorithm else True 
                    print("show algorithm: {}".format(Game.show_algorithm))

                # TODO can't get font resizing to work yet
#               font_changed = False
#               if mod and key.c == ord('=') and self.font_size_index < len(type(self).font_sizes) - 1:
#                       self.font_size_index += 1
#                       font_changed = True
#               if mod and key.c == ord('-') and self.font_size_index > 0:
#                       self.font_size_index -= 1
#                       font_changed = True
#               if font_changed:
#                   print('set font')
#                   font_path = os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'.format(size=type(self).font_sizes[self.font_size_index]))
#                   print(font_path)
#                   libtcod.console_set_custom_font(
#                           font_path, 
#                           libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
#                   libtcod.console_init_root(type(self).screen_width, type(self).screen_height, 'Cave Dweller', False)

