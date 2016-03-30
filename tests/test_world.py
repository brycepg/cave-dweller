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

from world import World
from block import Block, DuplicateBlockError
from game import Game
from entities import Player, Entity
from mocks import SerializerMock, StatusBarMock
import entities
import actions
import gen_map
import tiles
from tiles import Id

from test_gen_map import zero_map, obs_map

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
