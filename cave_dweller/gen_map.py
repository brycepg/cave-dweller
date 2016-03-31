#!/usr/bin/env python3

import random
import math

import libtcodpy as libtcod

import mynoise
#import noise
from mynoise import snoise2
from mynoise import snoise3
from tiles import Id
from tiles import Tiles

from game import Game


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


#def generate_block(seed, idx=0, idy=0, octaves=8,
#        # Function definition optimization arguments
#        map_size=Game.map_size,
#        rnd_seed=random.seed, range_size=range(Game.map_size), list_base=[None], div_range=map(lambda elem: elem/128., range(Game.map_size)),
#        any_ground=Id.any_ground, gnd_len=len(Id.any_ground),
#        wall=Id.wall, snoise2=snoise2, int=int,
#        random_float=random.random):
#    """Block generation algorithm using simplex noise
#
#    arguments
#        seed
#            Seed the block by using an offset factor
#
#        idx, idy
#            blocks unique id. contiguous. idy positive is down
#
#        map_size
#            size of block.
#
#        octaves
#            Number of simplex function passes for factal brownian motion.
#
#    returns
#        A 2d list of ints corresponsing to tile ID's. Column-major.
#    """
#    # Seed random with block seed for consistent results
#    rnd_seed(seed)
#    block = [list_base * map_size for _ in range_size]
#    idx_abs_base_scaled = (idx * map_size) / 128.
#    idy_abs_base_scaled = (idy * map_size) / 128.
#    for x in range_size:
#        x_scaled = x/128.
#        for y in range_size:
#            # Divide by scaling factor
#            # For some reason using tiling makes it look better?
#            # Making the seed a float changes behavior?
#            val = snoise2(x_scaled + idx_abs_base_scaled, idy_abs_base_scaled + div_range[y], octaves, base=seed, repeatx=65536, repeaty=65536)
#            # Can be tweaked for more / less floor/ground
#            if -.2 < val < 0:
#                # Floor tiles
#                block[x][y] = any_ground[int(random_float() * gnd_len)]
#            else:
#                # Wall tile
#                block[x][y] = wall
#    return block


## ----------------------Code below is not in use in game----------------------

def write_map(block, idx=0, idy=0, path=None):
    """Write map to file in pgm format"""
    if not path:
        pgm_out_path = ''.join(['map_', str(idx), 'x', str(idy), '.pgm'])
    else:
        pgm_out_path = path

    with open(pgm_out_path, 'wt') as pgm_out:
        pgm_out.write('P2\n')
        pgm_out.write('{blksz} {blksz}\n'.format(blksz=len(block)))
        pgm_out.write('255\n')
        for x_line in block:
            for x in x_line:
                out = 255 if x == 0 else 0
                pgm_out.write("%s\n" % out)


def block_snoise3(seed=0.0, idx=0, idy=0, map_size=96, octaves=8):
    """use snoise3 for block generation

    seed
        needs to be float. Use z axis of snoise3 as the seed. a whole number
        difference is big enough to not have much in common with the previous

    octaves
      increase to increaase detail/roughness
    """
    size = range(map_size)
    block = []
    append_blk = block.append
    any_ground = Id.any_ground
    chose = random.choice
    wall = Id.wall
    for x in size:
        y_line = []
        append = y_line.append
        for y in size:
            val = snoise3((idx * map_size + x) / 256.,
                          (idy * map_size + y) / 256.,
                          z=seed, octaves=octaves)
            # Can be tweaked for more / less floor/ground
            if -0.2 < val < 0.0:
                # Floor tiles
                append(chose(any_ground))
            else:
                # Wall tile
                append(wall)
        append_blk(y_line)
    return block


class BlockGenerator(object):
    """Using libtcod libraries instead of noise"""

    def __init__(self, seed):
        self.my_random = libtcod.random_new_from_seed(seed, algo=libtcod.RNG_CMWC)
        self.noise2d = libtcod.noise_new(2, random=self.my_random)

    def generate_block(self, idx=0, idy=0, map_size=256):
        """Block generation algorithm using simplex noise"""
        octaves = 8
        scaling_factor = 16.0 * octaves
        block = []
        size = range(map_size)
        append_blk = block.append
        any_ground = Id.any_ground
        chose = random.choice
        wall = Id.wall
        noise2d = self.noise2d
        for x in size:
            y_line = []
            append = y_line.append
            for y in size:
                val = libtcod.noise_get_fbm(noise2d, [(idx * map_size + x) / scaling_factor,
                              (idy * map_size + y) / scaling_factor],
                              octaves)
                # Can be tweaked for more / less floor/ground
                if -.2 < val < 0:
                    # Floor tiles
                    append(chose(any_ground))
                else:
                    # Wall tile
                    append(wall)
            append_blk(y_line)
        return block

    def disable(self):
        libtcod.noise_delete(self.noise2d)
        libtcod.random_delete(self.my_random)



def gen_tuneable(seed=0., idx=0, idy=0, map_size=96, octaves=8):
    """Block generation algorithm using simplex noise"""
    scaling_factor = 128.
    size = range(map_size)
    block = []
    append_blk = block.append
    any_ground = Id.any_ground
    chose = random.choice
    wall = Id.wall
    for x in size:
        y_line = []
        append = y_line.append
        for y in size:
            val = snoise2((idx * map_size + x) / scaling_factor,
                          (idy * map_size + y) / scaling_factor,
                          octaves, base=seed)
            # Can be tweaked for more / less floor/ground
            if -.2 < val < 0:
                # Floor tiles
                append(chose(any_ground))
            else:
                # Wall tile
                append(wall)
        append_blk(y_line)
    return block


def tune_block_snoise3(seed=0.0, idx=0, idy=0, map_size=96, octaves=8, lacunarity=2.0, persistence=0.5, min_val=-.2, max_val=0):
    """Tunable test for using 3d simplex noise for better seeds"""
    scaling_factor = 128.
    size = range(map_size)
    block = []
    append_blk = block.append
    any_ground = Id.any_ground
    chose = random.choice
    wall = Id.wall
    for x in size:
        y_line = []
        append = y_line.append
        for y in size:
            val = snoise3((idx * map_size + x) / scaling_factor,
                          (idy * map_size + y) / scaling_factor,
                          z=seed, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
            # Can be tweaked for more / less floor/ground
            if min_val < val < -0.2 < max_val:
                # Floor tiles
                append(chose(any_ground))
            else:
                # Wall tile
                append(wall)
        append_blk(y_line)
    return block
