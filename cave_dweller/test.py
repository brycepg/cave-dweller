import unittest
import random

from game import Game
from gen_map import generate_block

class TestDraw(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_draw(self):
        pass

zero_map = eval(open('zero_map.txt', 'r').read())
class TestGenerateMap(unittest.TestCase):
    def setUp(self):
        set_up_map()
    def tearDown(self):
        pass
    def test_gen_map(self):
        self.assertTrue(zero_map, generate_block(0, 0, 0, 96))

def set_up_map():
    random.seed(0)

def test_benchmark_map(benchmark):
    benchmark.pedantic(generate_block, args=(0, 0, 0, 96), setup=set_up_map, rounds=100)
if __name__ == "__main__":
    unittest.main()
