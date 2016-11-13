import os
import unittest
import random
import time
import operator
import math
import operator
import copy
import itertools

import sys
if __name__ == "__main__":
    sys.path.append("cave_dweller/")
    # mynoise
    sys.path.append(".")
import mynoise
import libtcodpy as libtcod

from cave_dweller.world import World
from cave_dweller.block import Block, DuplicateBlockError
from cave_dweller.game import Game
from cave_dweller.entities import Player, Entity
from cave_dweller.tiles import Id
from cave_dweller import entities
from cave_dweller import actions
from cave_dweller import gen_map
from cave_dweller import tiles

from .mocks import SerializerMock, StatusBarMock
from .test_gen_map import zero_map, obs_map

class TestWorld(unittest.TestCase):
    def setUp(self):
        pass

    def test_seeds(self):
        world = World(None)
        random.seed(0)
        seed_str, seed_float = world.generate_seeds()
        self.assertTrue(seed_str is None)
        self.assertTrue(type(seed_float) is float)
    def test_seed_str(self):
        world = World(None)
        seed_str, seed_float = world.generate_seeds("foo")
        self.assertEqual(seed_str, "foo")
        self.assertTrue(type(seed_float) is float)

    def test_seed_float(self):
        world = World(None)
        seed_str, seed_float = world.generate_seeds(seed_float=5)
        self.assertTrue(seed_str is None)
        self.assertEqual(seed_float, 5)

    def test_inspect(self):
        pass
