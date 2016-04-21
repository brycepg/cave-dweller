#!/usr/bin/env python3
"""Map generation functions"""

import random

from . import libtcodpy as libtcod

import mynoise
#import noise
from mynoise import snoise2
from mynoise import snoise3
from .tiles import Id
from .tiles import Tiles


def gen_map(seed, idx, idy, map_size=96,
    # Redefine globals as locals at definition time for optimization
    len=len, int=int, rnd_float=random.random, any_ground=Id.any_ground, gnd_len=len(Id.any_ground), range=range, gen_block=mynoise.gen_block, wall=Id.wall, rnd_seed=random.seed):
    """Generate map of size map_size for seed at (idx,idy)

    returns a 2d list of Tile ids
    """
    rnd_seed(seed)
    simplex_map = gen_block(seed, idx, idy, map_size)
    y_range = range(map_size)
    for x in xrange(map_size):
        simplex_slice = simplex_map[x]
        for y in y_range:
            if -.2 < simplex_slice[y] < 0:
                # Randomly choose ground tile
                simplex_slice[y] = any_ground[int(rnd_float() * gnd_len)]
            else:
                simplex_slice[y] = wall
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
