import os
import unittest
import random
import time
import operator
import math
import operator
import copy
import itertools

from cave_dweller import libtcodpy as libtcod

from cave_dweller.world import World
from cave_dweller.block import Block, DuplicateBlockError
from cave_dweller.game import Game
from cave_dweller.entities import Player
from cave_dweller.tiles import Id
from cave_dweller import entities
from cave_dweller import actions
from cave_dweller import gen_map

from .mocks import SerializerMock, StatusBarMock
from .test_gen_map import zero_map, obs_map
from . import test_block
def test_block_load_surround(benchmark):
    s_mock = SerializerMock()
    w = World(s_mock, block_seed=0)
    benchmark.pedantic(w.load_surrounding_blocks, args=(0, 0), rounds=1)

#def test_block_process(benchmark):
#    s_mock = SerializerMock()
#    w = World(s_mock, block_seed=0)
#    w.load_surrounding_blocks(0, 0)
#    benchmark.pedantic(w.process, rounds=1)

en = [entities.Cat, entities.Spider, entities.Mole, entities.Fungus]
def rand_entities():
    empty_map = gen_map.gen_empty_entities(Game.map_size)
    for x in range(Game.map_size):
        for y in range(Game.map_size):
            if x % 2 and y % 2 and x != 0 and y != 0 and y != Game.map_size-1 and x != Game.map_size -1:
                empty_map[x][y].append(random.choice(en)(x, y))
    return empty_map
def test_block_process_big(benchmark):
    s_mock = SerializerMock()
    w = World(s_mock, block_seed=0)
    locs = itertools.product([1,0,-1], [1,0,-1])
    for loc in locs:
        w.blocks[loc] = Block(*loc, world=w,
                                  tiles=test_block.gen_flat_map(Game.map_size),
                                  entities=rand_entities())
    benchmark.pedantic(w.process, rounds=1)

#reduce(operator.add, [len(w.get(*key).entity_list) for key in w.blocks])
