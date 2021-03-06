import os
import unittest
import random
import time
import tempfile
import operator
import math
from ctypes import c_float

from PIL import Image
import sys
#p = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(p)
from cave_dweller import libtcodpy as libtcod
from cave_dweller.libtcodpy import _lib
console_flush = _lib.TCOD_console_flush

from cave_dweller.world import World
from cave_dweller.game import Game
from cave_dweller.entities import Player
from cave_dweller.font_handler import FontHandler
from cave_dweller import actions
from cave_dweller import block
from cave_dweller import tiles

from .mocks import SerializerMock, StatusBarMock
cur_dir = os.path.dirname(__file__)
SCREENSHOT_TEST_PATH = os.path.join(cur_dir, "screenshot5.bmp")

def img_rms_diff(img1, img2):
    h1 = img1.histogram()
    h2 = img2.histogram()
    # Take the root mean square of each image's histogram.
    # map both histograms into one list via elementwise difference squared.
    # use reduce to sum the resultant list to one value and take the average
    # Then take the square root
    rms = math.sqrt(reduce(operator.add,
        map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
    print(rms)
    return rms

class TestDraw(unittest.TestCase):
    # Only have one game becuase of inability for libtcod to deinit window
    # But only initalize it during set up(instead of statically)
    # Do allow it to close
    g = None
    @classmethod
    def set_game(cls):
        if not cls.g:
            fh = FontHandler(font_index=0)
            cls.g = Game(fh)


    def setUp(self):
        """Set up game/player to allow drawing"""
        self.__class__.set_game()
        Game.set_sidebar(False)
        s = SerializerMock()
        w = World(s, block_seed=0)
        start_block = w.get(Game.idx_cur, Game.idy_cur)
        player = start_block.set_entity(Player, Game.map_size//2, Game.map_size//2)
        # Potentially update player location
        start_block.reposition_entity(player, avoid_hidden=True)
        # Update view to player location
        player.update_view_location()

        status_bar_mock = StatusBarMock()
        self.status_bar_mock = status_bar_mock
        self.player = player
        self.w = w
        self.start_block = start_block
        self.console_flush = console_flush

    def test_screen_draw(self):
        """Compare current screen with past screenshot"""
        w = self.w
        g = self.__class__.g
        w.draw()
        g.blit_consoles(self.status_bar_mock)
        self.console_flush()

        with tempfile.NamedTemporaryFile() as my_tempfile:
            libtcod.sys_save_screenshot(my_tempfile.name)
            dynamic_img = Image.open(my_tempfile.name)
            old_img = Image.open(SCREENSHOT_TEST_PATH)
            rms = img_rms_diff(old_img, dynamic_img)
            self.assertEqual(rms, 0)
            self.assertEqual(dynamic_img.tobytes(), old_img.tobytes())

    def test_screen_movement(self):
        player = self.player
        start_block = self.start_block
        w = self.w
        g = self.__class__.g

        a = actions.Move()
        a.dir_dict['right'] = True
        a.dir('right', (player.x+1, player.y), start_block, player)

        w.draw()
        g.blit_consoles(self.status_bar_mock)
        self.console_flush()

        with tempfile.NamedTemporaryFile() as my_tempfile:
            libtcod.sys_save_screenshot(my_tempfile.name)
            dynamic_img = Image.open(my_tempfile.name)
            old_img = Image.open(SCREENSHOT_TEST_PATH)
            rms = img_rms_diff(old_img, dynamic_img)
            # Same color content, different positions
            self.assertEqual(rms, 0)
            self.assertNotEqual(dynamic_img.tobytes(), old_img.tobytes())

    def test_draw_bg(self):
        w = self.w
        start_block = self.start_block
        dc1 = DrawCapture()

        block_abs_x_min = Game.map_size * start_block.idx
        block_abs_y_min = Game.map_size * start_block.idy
        # Comparison between view edge and edge of block
        draw_x_min_abs = max(block_abs_x_min, Game.min_x)
        draw_y_min_abs = max(block_abs_y_min, Game.min_y)
        # Put pack into block coordinates
        loc_x_min = draw_x_min_abs % Game.map_size
        loc_y_min = draw_y_min_abs % Game.map_size

        start_block.hidden_map[loc_x_min][loc_y_min] = False
        self.assertEqual((0,0), start_block.get_drawable_coordinate(loc_x_min, loc_y_min))
        wtf_color = libtcod.Color(133,71,33)
        start_block.draw_block(put_char_ex=dc1.draw_capture)
        self.assertNotEqual(wtf_color, dc1.capture_array[0][5])

        dc2 = DrawCapture()
        player = start_block.set_entity(Player, loc_x_min, loc_y_min)
        player.bg = wtf_color
        start_block.draw_block(put_char_ex=dc2.draw_capture)
        self.assertEqual(wtf_color, dc2.capture_array[0][5])

class DrawCapture(object):
    def __init__(self):
        self.capture_array = []

    def draw_capture(self, *args):
        self.capture_array.append(args)
