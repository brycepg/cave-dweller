import os
import unittest
import random
import copy

from cave_dweller.gen_map import generate_obstacle_map
from cave_dweller.gen_map import gen_map as generate_block
from cave_dweller.tiles import Tiles

cur_dir = os.path.dirname(__file__)
map_size = 96

zero_map = eval(open(os.path.join(cur_dir, 'zero_map.txt'), 'r').read())
obs_map = eval(open(os.path.join(cur_dir, "zero_map_obs.txt"), 'r').read())
def normalize_map(block_map_ref):
    """Replace all ground variations with 0 ground type"""
    block_map = copy.deepcopy(block_map_ref)
    for y in range(len(block_map)):
        for x in range(len(block_map)):
            if block_map[x][y] <= 3:
                block_map[x][y] = 0
    return block_map
class TestGenerateMap(unittest.TestCase):
    def test_gen_map(self):
        # Test normalized map first -- ground blocks are converged to one value
        self.assertEqual(normalize_map(zero_map), normalize_map(generate_block(0, 0, 0)))
        # Then test individual blocks
        self.assertEqual(zero_map, generate_block(0, 0, 0))
        # Uses random number generator -- seed inside
        self.assertEqual(zero_map, generate_block(0, 0, 0))
        self.assertNotEqual(zero_map, generate_block(1, 0, 0))
        self.assertNotEqual(zero_map, generate_block(0, 1, 0))
        self.assertNotEqual(zero_map, generate_block(0, 0, 1))

    def test_generate_obs_map(self):
        self.assertEqual(obs_map, generate_obstacle_map(zero_map, map_size))
        for x in range(map_size):
            for y in range(map_size):
                self.assertEqual(obs_map[x][y], Tiles.tile_lookup[zero_map[x][y]].is_obstacle)

def write_zero_map(filepath):
    open(filepath).write(generate_block(0,0,0))

def write_obs_map(filepath):
    open(filepath).write(generate_obstacle_map(
        generate_block(0,0,0), len(generate_block(0,0,0))))

if __name__ == "__main__":
    unittest.main()
