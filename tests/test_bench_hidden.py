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
from test_block import gen_flat_map

def test_set_tile_open(benchmark):
    game = Game()
    w = World(None)
    locs = itertools.product([1,0,-1], [1,0,-1])
    flat_map = gen_flat_map(Game.map_size)
    for loc in locs:
        w.blocks[loc] = Block(*loc, world=w,
                                  tiles=gen_flat_map(Game.map_size),
                                  entities=gen_map.gen_empty_entities(Game.map_size))
    blk = w[(0,0)]
    benchmark.pedantic(blk.set_tile, args=(Game.game_width//2, Game.game_height//2, Id.wall), rounds=1)
