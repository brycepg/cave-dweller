import os
import unittest
import random

from gen_map import generate_block

cur_dir = os.path.dirname(__file__)

class TestDraw(unittest.TestCase):
    def setUp(self):
        pass
    def tearDown(self):
        pass
    def test_draw(self):
        pass

zero_map = eval(open(os.path.join(cur_dir, 'zero_map.txt'), 'r').read())
class TestGenerateMap(unittest.TestCase):
    def setUp(self):
        set_up_map()
    def tearDown(self):
        pass
    def test_gen_map(self):
        self.assertEqual(zero_map, generate_block(0, 0, 0, 96))
        # Uses random number generator for picking ground tile chars
        self.assertNotEqual(zero_map, generate_block(0, 0, 0, 96))

def set_up_map():
    random.seed(0)

if __name__ == "__main__":
    unittest.main()
