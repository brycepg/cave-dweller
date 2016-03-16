import unittest
import random

from game import Game
from gen_map import generate_block
from .test_gen_map import set_up_map

def test_benchmark_map(benchmark):
    # One time only
    set_up_map()
    benchmark(generate_block, 0, 0, 0, 96)
