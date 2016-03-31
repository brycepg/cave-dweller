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
import collections

# Add some paths for opening the file directly when profiling
if __name__ == "__main__":
    sys.path.append("cave_dweller/")
    # mynoise
    sys.path.append(".")
import libtcodpy as libtcod
import mynoise

import entities
import actions
import gen_map
import tiles
import util
from world import World
from block import Block, DuplicateBlockError
from game import Game
from entities import Player, Entity
from mocks import SerializerMock, StatusBarMock
from tiles import Id
import hidden_map_handler
from gen_map import generate_obstacle_map
from gen_map import gen_map as generate_map

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
            a_slice = blk.get_entities(*placement)
            self.assertTrue(fungus in a_slice)
            self.assertTrue(fungus is blk.get_entity(*placement))
            blk.remove_entity(fungus, *placement)
            self.assertFalse(fungus in f_blk.entities[x%Game.map_size][y%Game.map_size])
    def testBoundsMove(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        l = [Game.map_size, Game.map_size-1, 0, -1]
        bound_possibilities = itertools.product(l,l)
        prev_placement = (0,0)
        for placement in bound_possibilities:
            fungus = blk.set_entity(entities.Fungus, 0,0)
            blk.reposition_entity(fungus)
            self.assertTrue(fungus in blk.entities[0][0])

            blk.move_entity(fungus, *placement)
            x, y = placement
            f_blk = w.get(x// Game.map_size, y// Game.map_size)
            self.assertTrue(fungus in f_blk.entities[x%Game.map_size][y%Game.map_size])
            blk.remove_entity(fungus, *placement)
            self.assertFalse(fungus in f_blk.entities[x%Game.map_size][y%Game.map_size])

    def test_abs(self):
        w = self.w
        idx, idy = (0,0)
        blk = w.blocks[(idx, idy)]
        self.assertEqual(blk.get_abs(0,0), (0,0))
        self.assertEqual(blk.get_abs(90,94), (90,94))
        idx, idy = (2,3)
        blk = Block(idx, idy, w)
        self.assertEqual(blk.get_abs(0,0), (Game.map_size*idx, Game.map_size*idy))
        self.assertEqual(blk.get_abs(90,94), (Game.map_size*idx + 90,Game.map_size*idy + 94))

    def test_locate(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        loc = (4,4)
        fungus = blk.set_entity(entities.Fungus, *loc)
        self.assertEqual(loc, blk.locate(fungus))

    def test_hidden(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        loc = (0,0)
        self.assertFalse(blk.get_hidden(*loc))
        self.assertFalse(blk.hidden_map[loc[0]][loc[1]])
        blk.set_hidden(*loc, value=True)
        self.assertTrue(blk.get_hidden(*loc))
        self.assertTrue(blk.hidden_map[loc[0]][loc[1]])
        blk.set_hidden(*loc, value=False)
        self.assertFalse(blk.get_hidden(*loc))

        loc_mod = (Game.map_size, Game.map_size)
        blk_mod = w[(1,1)]
        self.assertFalse(blk.get_hidden(*loc_mod))
        self.assertFalse(blk_mod.hidden_map[0][0] )
        blk.set_hidden(*loc_mod, value=True)
        self.assertTrue(blk.get_hidden(*loc_mod))
        self.assertTrue(blk_mod.hidden_map[0][0] )
        blk.set_hidden(*loc_mod, value=False)
        self.assertFalse(blk.get_hidden(*loc_mod))
        self.assertFalse(blk_mod.hidden_map[0][0] )

    def test_process(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        loc = (0,0)
        mole = blk.set_entity(entities.Mole, *loc)
        w.process()
        self.assertFalse(mole.is_dead)
        mole_loc = (mole.x, mole.y)
        self.assertTrue(blk.locate(mole) == mole_loc)
        mole.kill()
        self.assertTrue(mole.is_dead)
        self.assertFalse(type(blk.get_entity(*mole_loc)) is entities.Fungus)
        for _ in range(Entity.DECOMPOSE_TIME):
            w.process()
        self.assertTrue(blk.locate(mole) is None)
        new_entity = blk.get_entity(*mole_loc)
        self.assertTrue(type(new_entity) is entities.Fungus)

    def test_obstacle(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        loc = (Game.map_size, Game.map_size)
        idx_div = lambda val: val // Game.map_size
        blk_outside = w[tuple(map(idx_div, loc))]
        self.assertFalse(blk_outside.obstacle_map[0][0])
        self.assertFalse(blk.is_obstacle(*loc))
        blk_outside.obstacle_map[0][0] = True
        self.assertTrue(blk.is_obstacle(*loc))

    def test_tile(self):
        w = self.w
        blk = w.blocks[(0, 0)]
        loc = (0,0)
        self.assertNotEqual(tiles.Tiles.tile_lookup[Id.wall], blk.get_tile(*loc))
        blk.set_tile(*loc, new_tile=Id.wall)
        self.assertEqual(tiles.Tiles.tile_lookup[Id.wall], blk.get_tile(*loc))

        loc = (Game.map_size,Game.map_size)
        self.assertNotEqual(tiles.Tiles.tile_lookup[Id.wall], blk.get_tile(*loc))
        blk.set_tile(*loc, new_tile=Id.wall)
        self.assertEqual(tiles.Tiles.tile_lookup[Id.wall], blk.get_tile(*loc))

    def test_hidden_update(self):
        self.__class__.set_game()
        g = self.__class__.g
        w = self.w
        blk = w.blocks[(0, 0)]
        locs = [(1,0), (1,2), (2,1), (0,1)]
        center_loc = (1,1)
        self.assertFalse(blk.get_hidden(*center_loc))
        for loc in locs:
            blk.set_tile(*loc, new_tile=Id.wall)
        self.assertTrue(blk.get_hidden(*center_loc))

    def test_entity_order(self):
        w = self.w
        blk = w.blocks[(0,0)]

        prev_turn = w.turn

        d = blk.set_entity(entities.Dummy, 0, 0)
        m = blk.set_entity(entities.Mole, 1, 0)

        self.assertFalse(d.is_dead)
        self.assertFalse(m.is_dead)
        d.queue_kill(entities.Direction.right)
        w.process()
        self.assertTrue(m.is_dead)
        self.assertEqual(m.last_move_turn, prev_turn)
        self.assertEqual(d.last_move_turn, prev_turn)
        d2 = blk.set_entity(entities.Dummy, -1, 0)
        d.queue_kill(entities.Direction.left)
        d2.queue_kill(entities.Direction.right)
        w.process()
        # Arbitrary order!
        # Based on the hash
        # XXX fix
        self.assertFalse(d.is_dead)
        self.assertTrue(d2.is_dead)

        d3 = blk.set_entity(entities.Dummy, 0, 2)
        d.queue_move(entities.Direction.down)
        d3.queue_move(entities.Direction.up)
        w.process()
        self.assertEqual((0, 1), (d.x, d.y))
        self.assertEqual((0, 2), (d3.x, d3.y))

    def test_spider(self):
        w = self.w
        blk = w.blocks[(0,0)]
        s = blk.set_entity(entities.Spider, 1, 0)
        m = blk.set_entity(entities.Mole, 2, 0)
        self.assertFalse(m.is_dead)
        w.process()
        self.assertTrue(m.is_dead)
        self.assertFalse(m not in blk.entity_list)
        while m.food > 0:
            w.process()
            self.assertTrue(m.is_dead)
        self.assertTrue(m not in blk.entity_list)
        s.hunger = s.MAX_HUNGER
        m = blk.set_entity(entities.Mole, 2, 0)
        c = collections.Counter([type(entity) for entity in blk.entity_list])
        self.assertEqual(c[entities.Spider], 1)
        self.assertEqual(c[entities.Mole], 1)
        while m.food > 0:
            w.process()
            self.assertTrue(m.is_dead)
        c = collections.Counter([type(entity) for entity in blk.entity_list])
        self.assertEqual(c[entities.Spider], 2)

        while s.hunger > 0:
            w.process()
        self.assertTrue(s.is_dead)

    def test_mole(self):
        w = self.w
        blk = w.blocks[(0,0)]
        m = blk.set_entity(entities.Mole, 0, 0)
        c = util.count_entities(blk)
        self.assertEqual(c[entities.Mole], 1)
        self.assertEqual(c[entities.Fungus], 0)
        for x in range(1, 92):
            m = blk.set_entity(entities.Fungus, x, 0)
            w.process()
        c = util.count_entities(blk)
        self.assertEqual(c[entities.Mole], 2)
        self.assertEqual(c[entities.Fungus], 0)

class TestFlatMapsDraw(unittest.TestCase):

    g = None
    @classmethod
    def set_game(cls):
        if not cls.g:
            cls.g = Game()

    def setUp(self):
        super(TestFlatMapsDraw, self).setUp()
        self.__class__.set_game()
        s_mock = SerializerMock()
        self.w = World(s_mock, block_seed=0)
        # Cartesian product
        locs = itertools.product([1,0,-1], [1,0,-1])
        flat_map = gen_flat_map(Game.map_size)
        for loc in locs:
            self.w.blocks[loc] = Block(*loc, world=self.w,
                                      tiles=gen_flat_map(Game.map_size),
                                      entities=gen_map.gen_empty_entities(Game.map_size))

    def test_hidden_multi_block(self):
        # Merge tests together because this test suite is getting too slow
        w = self.w
        blk = w.blocks[(0, 0)]
        locs = [(0,0), (0,2), (1,1), (-1,1)]
        Game.view_x = -1
        Game.view_y = -1
        center_loc = (0,1)
        self.assertFalse(blk.get_hidden(*center_loc))
        for loc in locs:
            blk.set_tile(*loc, new_tile=Id.wall)
        self.assertTrue(blk.get_hidden(*center_loc))

        # test hidden large area 2x2 inside
        modifier_x = 3
        inside = [(1,1), (1,2), (2,1), (2,2)]
        inside = [(x+modifier_x, y) for x,y in inside]
        locs = [(1,0), (2,0),
              (0,1), (3,1),
              (0,2), (3,2),
              (1,3), (2,3)]
        locs = [(x+modifier_x, y) for x,y in locs]

        for loc in inside:
            self.assertFalse(blk.get_hidden(*loc))
        for loc in locs:
            blk.set_tile(*loc, new_tile=Id.wall)
        for loc in inside:
            self.assertTrue(blk.get_hidden(*loc))

        # Remove one tile to reveal hidden
        blk.set_tile(*locs[0], new_tile=Id.ground)
        for loc in inside:
            self.assertFalse(blk.get_hidden(*loc))

        # test_hidden_skinny
        modifier_x = 8
        inside = [(1,1), (1,2)]
        inside = [(x+modifier_x, y) for x,y in inside]
        locs = [(1,0),
                (0,1), (2,1),
                (0,2), (2,2),
                (1,3)]
        locs = [(x+modifier_x, y) for x,y in locs]
        for loc in inside:
            self.assertFalse(blk.get_hidden(*loc))
        for loc in locs:
            blk.set_tile(*loc, new_tile=Id.wall)
        for loc in inside:
            self.assertTrue(blk.get_hidden(*loc))

class TestWorldEmpty(unittest.TestCase):
    def test_block_args(self):
        s_mock = SerializerMock()
        w = World(s_mock, block_seed=0)
        blk = Block(0, 0, w)
        tiles = generate_map(w.seed_float, 0, 0)
        hidden_map = hidden_map_handler.generate_map(Game.map_size)
        obstacle_map = generate_obstacle_map(tiles, Game.map_size)
        blk2 = Block(0, 0, w, hidden_map=hidden_map,
                     obstacle_map=obstacle_map, tiles=tiles)
        self.assertEqual(blk, blk2)

def draw_here(w, g=None):
    if not g:
        g = Game()
    w.draw()
    g.blit_consoles(None)
    libtcod.console_flush()


import cProfile
if __name__ == "__main__":
    suite = unittest.TestLoader().discover('.')
    def runtests():
        unittest.TextTestRunner().run(suite)
    if len(sys.argv) > 1 and sys.argv[1] == "-p":
        s = cProfile.run('runtests()', sort='cumtime')
    else:
        runtests()
