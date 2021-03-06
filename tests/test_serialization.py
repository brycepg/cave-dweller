"""Test the serializer"""
import os
import unittest
import sys
import shutil

# Add some paths for opening the file directly when profiling
if __name__ == "__main__":
    sys.path.append("cave_dweller/")
    # mynoise
    sys.path.append(".")
import libtcodpy as libtcod

from cave_dweller import entities
from cave_dweller import actions
from cave_dweller import gen_map
from cave_dweller import tiles
from cave_dweller import hidden_map_handler
from cave_dweller import serializer
from cave_dweller import util
from cave_dweller.world import World
from cave_dweller.block import Block, DuplicateBlockError
from cave_dweller.game import Game
from cave_dweller.entities import Player, Entity
from cave_dweller.tiles import Id
from cave_dweller.gen_map import generate_obstacle_map
from cave_dweller.gen_map import gen_map as generate_map

class TestSerialization(unittest.TestCase):
    def test_serialization(self):
        basedir = util.game_path('test_data_dir')
        s = serializer.Serializer(basedir=basedir)
        folder = s.folder_name
        w = World(s, block_seed=0)
        b = w.get(0,0)
        p = b.set_entity(entities.Player, 3, 7)
        p_x, p_y = p.x, p.y
        for _ in range(2):
            w.process()
        self.assertEqual(w.turn, 2)
        turn = w.turn
        self.assertFalse(s.has_settings())
        s.save_game(w, p)
        self.assertTrue(s.has_settings())
        s.close_connection()
        del w
        del b
        del p
        del s
        s = serializer.Serializer(basedir=basedir, folder=folder)
        s.load_settings()
        w = s.init_world()
        self.assertEqual(turn, w.turn)
        p = s.init_player(w)
        self.assertEqual((p_x, p_y), (p.x, p.y))
        b = w[(0, 0)]
        c = util.count_entities(b)
        self.assertEqual(c[entities.Player], 1)
        shutil.rmtree(s.serial_path)
        shutil.rmtree(basedir)

    def test_no_folder(self):
        basedir = util.game_path('test_data_dir')
        with self.assertRaises(RuntimeError):
            s = serializer.Serializer(basedir=basedir, folder="foo")

import cProfile
if __name__ == "__main__":
    suite = unittest.TestLoader().discover('.')
    def runtests():
        unittest.TextTestRunner().run(suite)
    if len(sys.argv) > 1 and sys.argv[1] == "-p":
        cProfile.run('runtests()', sort='cumtime')
    else:
        runtests()
