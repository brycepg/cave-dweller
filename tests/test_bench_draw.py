import os
import unittest
import random
import time
import tempfile
import operator
import math
from ctypes import c_float

from PIL import Image
from libtcodpy import _lib
console_flush = _lib.TCOD_console_flush

from cave_dweller.world import World
from cave_dweller.game import Game
from cave_dweller.entities import Player
from cave_dweller import libtcodpy as libtcod
from cave_dweller import actions

from .mocks import SerializerMock, StatusBarMock

cur_dir = os.path.dirname(__file__)
SCREENSHOT_TEST_PATH = os.path.join(cur_dir, "screenshot3.bmp")

def test_world_draw(benchmark):
    """Compare current screen with past screenshot"""
    g = Game()

    Game.set_sidebar(False)
    s = SerializerMock()
    w = World(s, block_seed=0)
    block = w.get(Game.idx_cur, Game.idy_cur)
    player = block.set_entity(Player, Game.map_size//2, Game.map_size//2)
    # Potentially update player location
    block.reposition_entity(player, avoid_hidden=True)
    # Update view to player location
    player.update_view_location()
    benchmark(w.draw)
    #the_rest()

def the_rest():
    Game.blit_consoles(None)
    libtcod.console_flush()
