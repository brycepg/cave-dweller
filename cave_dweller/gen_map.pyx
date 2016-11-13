#!/usr/bin/env python3
"""Map generation functions"""
from cython.operator cimport dereference

import random

from . import libtcodpy as libtcod

import mynoise
#import noise
from mynoise import snoise2
from mynoise import snoise3
from .tiles import Id
from .tiles import Tiles

cdef extern from "trng/mt19937.hpp" namespace "trng":
    cdef cppclass mt19937:
        mt19937()
        mt19937(unsigned long)

cdef extern from "trng/uniform_int_dist.hpp" namespace "trng":
    cdef cppclass uniform_int_dist:
        uniform_int_dist()
        uniform_int_dist(int, int)
        #uniform_int_dist(const param_type &)
        #int operator()(R &, const param_type &);
        int operator()(mt19937); 

#cdef extern from "stdlib.h":
#    int RAND_MAX
#    void srand(unsigned int)
#    int rand()

cdef uniform_int_dist U = uniform_int_dist(0,3)
def gen_map(float seed, int idx, int idy, int map_size=96):
    # Redefine globals as locals at definition time for optimization
    """Generate map of size map_size for seed at (idx,idy)

    returns a 2d list of Tile ids
    """
    # Negative seeds wrap-around
    cdef int gnd_len=len(Id.any_ground)
    cdef mt19937 M = mt19937(<unsigned long>seed)
    simplex_map = mynoise.gen_block(seed, idx, idy, map_size)
    for x in xrange(map_size):
        for y in xrange(map_size):
            if -.2 < simplex_map[x][y] < 0:
                # Randomly choose ground tile
                # Use higher order bits of rand(may not be completly uniform but 
                # that doesn't matter for choosing ground tiles)
                #simplex_map[x][y] = Id.any_ground[(rand() / (RAND_MAX / gnd_len + 1))]
                #simplex_map[x][y] = Id.any_ground[0]
                simplex_map[x][y] = Id.any_ground[U(M)]
            else:
                simplex_map[x][y] = Id.wall
    return simplex_map


def generate_obstacle_map(tiles, map_size):
    """Generates map of tiles that are obstacles.
       Entities are added onto the map as they are generated later"""
    obstacle_map = []
    list_append = obstacle_map.append
    tile_lookup = Tiles.tile_lookup
    for x in range(map_size):
        x_slice = []
        cell_append = x_slice.append
        tile_slice = tiles[x]
        for y in range(map_size):
            if tile_lookup[tile_slice[y]].is_obstacle:
                cell_append(True)
            else:
                cell_append(False)
        list_append(x_slice)
    return obstacle_map


def string_seed(my_str):
    """Quick 'hashing' of string to float"""
    my_hash = 0.
    for char in my_str:
        my_hash = 31 * my_hash + ord(char)
    # Seeds don't work above this number
    return my_hash % 65536


def gen_empty_entities(map_size):
    return [[[] for _ in range(map_size)] for _ in range(map_size)]
