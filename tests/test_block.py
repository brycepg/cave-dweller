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
from entities import Player
from mocks import SerializerMock, StatusBarMock
import entities
import actions
import gen_map
from tiles import Id


from test_gen_map import zero_map, obs_map

class TestBlock(unittest.TestCase):
    def setUp(self):
        s_mock = SerializerMock()
        self.w = World(s_mock, block_seed=0)
        self.zero_blk = self.w.get(0, 0)
    def testMaps(self):
        self.assertEqual(self.zero_blk.tiles, zero_map)
        # Where the obstacle map does not match the gen_map obstacle map,
        # Make sure there is an entity located there
        obs_entities = [ (x,y) for x in range(len(obs_map)) for y in range(len(obs_map)) if obs_map[x][y] != self.zero_blk.obstacle_map[x][y]]
        for entity_loc in obs_entities:
            obstacle_entity = any([entity.is_obstacle for entity in self.zero_blk.entities[entity_loc[0]][entity_loc[1]]])
            self.assertTrue(obstacle_entity)

        self.assertNotEqual(self.zero_blk.obstacle_map, obs_map)
    def testEntities(self):
        flat_list = [entity for a_slice in self.zero_blk.entities for a_cell in a_slice for entity in a_cell]
        flat_list_set = set(flat_list)
        entity_list_set = set(self.zero_blk.entity_list)
        self.assertEqual(flat_list_set, entity_list_set)
        fungus = self.zero_blk.set_entity(entities.Fungus, 0, 0)
        self.assertTrue(fungus in self.zero_blk.entities[0][0])

        # Add an entity
        n_flat_list = [entity for a_slice in self.zero_blk.entities for a_cell in a_slice for entity in a_cell]
        n_flat_list_set = set(n_flat_list)
        n_entity_list_set = set(self.zero_blk.entity_list)
        self.assertEqual(n_flat_list_set, n_entity_list_set)
        self.assertNotEqual(flat_list_set, n_flat_list_set)
        self.assertNotEqual(entity_list_set, n_entity_list_set)

        # Get entity
        self.assertEqual(fungus, self.zero_blk.get_entity(0, 0))
        self.assertEqual([fungus], self.zero_blk.get_entities(0, 0))


        # Remove the entity
        self.zero_blk.remove_entity(fungus, 0, 0)
        self.assertFalse(fungus in self.zero_blk.entities[0][0])
        with self.assertRaises(ValueError):
            self.zero_blk.remove_entity(fungus, 0, 0)

        # Get empty
        self.assertEqual(None, self.zero_blk.get_entity(0, 0))
        self.assertEqual([], self.zero_blk.get_entities(0, 0))

        n2_flat_list = [entity for a_slice in self.zero_blk.entities for a_cell in a_slice for entity in a_cell]
        n2_flat_list_set = set(n2_flat_list)
        n2_entity_list_set = set(self.zero_blk.entity_list)
        self.assertEqual(n2_flat_list_set, n2_entity_list_set)
        self.assertNotEqual(n2_flat_list_set, n_flat_list_set)
        self.assertNotEqual(n2_entity_list_set, n_entity_list_set)
        self.assertEqual(n2_flat_list_set, flat_list_set)
        self.assertEqual(n2_entity_list_set, entity_list_set)

    def testMoveEntity(self):
        movements = ((1, 0), (-1, 0), (0, 1), (0, -1))
        for move in movements:
            fungus = self.zero_blk.set_entity(entities.Fungus, Game.map_size//2, Game.map_size//2)
            self.zero_blk.reposition_entity(fungus)
            (old_x,old_y) = fungus.x, fungus.y
            self.zero_blk.move_entity(fungus, *map(operator.add, move, (fungus.x, fungus.y)))
            self.assertEqual(map(operator.add, move, (old_x, old_y)), [fungus.x, fungus.y])
            self.assertFalse(fungus in self.zero_blk.entities[old_x][old_y])
            self.assertTrue(fungus in self.zero_blk.entities[fungus.x][fungus.y])
            self.assertTrue(fungus in self.zero_blk.entity_list)
            self.zero_blk.remove_entity(fungus, fungus.x, fungus.y)

    def testDuplicateBlock(self):
        """Test duplicate block check with DuplicateBlockError exception"""
        with self.assertRaises(DuplicateBlockError) as exception:
            b = Block(0, 0, self.w)

        ex = exception.exception
        self.assertEqual(ex.idx, 0)
        self.assertEqual(ex.idy, 0)

def gen_flat_map(map_size):
    return [[Id.ground] * map_size for _ in range(map_size)]

class TestFlatMaps(unittest.TestCase):

    g = None
    @classmethod
    def set_game(cls):
        if not cls.g:
            cls.g = Game()

    def setUp(self):
        s_mock = SerializerMock()
        self.w = World(s_mock, block_seed=0)
        # Cartesian product
        locs = itertools.product([1,0,-1], [1,0,-1])
        flat_map = gen_flat_map(Game.map_size)
        for loc in locs:
            self.w.blocks[loc] = Block(*loc, world=self.w,
                                      tiles=gen_flat_map(Game.map_size),
                                      entities=gen_map.gen_empty_entities(Game.map_size))

    def testBounds(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        l = [Game.map_size, Game.map_size-1, 0, -1]
        bound_possibilities = itertools.product(l,l)
        for placement in bound_possibilities:
            fungus = blk.set_entity(entities.Fungus, *placement)
            x, y = placement
            f_blk = w.get(x// Game.map_size, y// Game.map_size)
            self.assertTrue(fungus in f_blk.entities[x%Game.map_size][y%Game.map_size])
            blk.remove_entity(fungus, *placement)
            self.assertFalse(fungus in f_blk.entities[x%Game.map_size][y%Game.map_size])



if __name__ == "__main__":
    uittest.main()
