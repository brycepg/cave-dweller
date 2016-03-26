import unittest
import random

from game import Game
#from gen_map import generate_block
from gen_map import gen_map as c_gen_map
from gen_map import generate_obstacle_map
from .test_gen_map import zero_map, obs_map

def test_benchmark_map(benchmark):
    # One time only
    result = benchmark.pedantic(c_gen_map, args=(0, 0, 0), rounds=50)
    assert result == zero_map

#def test_c_gen_map(benchmark):
#    result = benchmark.pedantic(c_gen_map, args=(0, 0, 0), rounds=50)
#    assert result == zero_map

def test_benchmark_obstacle_map(benchmark):
    # One time only
    result = benchmark.pedantic(generate_obstacle_map, args=(zero_map, 96), rounds=50)
    assert result == obs_map
