#!/usr/bin/env python3

import random
import math

import libtcodpy as libtcod

from noise import snoise2
from noise import snoise3
from tiles import Id
from tiles import Tiles

def generate_block(seed, idx=0, idy=0, map_size=256, octaves=8):
    """Block generation algorithm using simplex noise
    
    seed
        Seed the block by using an offset factor
    
    idx, idy
        blocks unique id. contiguous. idy positive is down

    map_size
        size of block

    octaves
        # of simplex fxn passes for factal brownian motion
    """
    block = []
    size = range(map_size)
    append_blk = block.append
    any_ground = Id.any_ground 
    chose = random.choice 
    wall = Id.wall
    for x in size:
        y_line = []
        append = y_line.append
        for y in size:
            # Divide by scaling factor
            # For some reason using tiling makes it look better?
            # Making the seed a float changes behavior?
            # WTF
            val = snoise2((idx * map_size + x) / 128.,
                          (idy * map_size + y) / 128.,
                          octaves, base=seed,
                          repeatx=65536,
                          repeaty=65536)
            # Can be tweaked for more / less floor/ground
            if -.2 < val < 0:
                # Floor tiles 
                append(chose(any_ground))
            else:
                # Wall tile
                append(wall)
        append_blk(y_line)
    return block


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
