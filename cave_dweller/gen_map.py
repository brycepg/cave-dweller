#!/usr/bin/env python3

import random

import libtcodpy as libtcod

from noise import snoise2
from tiles import Id
from tiles import Tiles

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


def generate_block(seed, idx=0, idy=0, map_size=256):
    """Block generation algorithm using simplex noise"""
    octaves = 8
    freq = 16.0 * octaves
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
            val = snoise2((idx * map_size + x) / freq,
                          (idy * map_size + y) / freq,
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

class BlockGenerator(object):
    """Using libtcod libraries instead of noise"""

    def __init__(self, seed):
        self.my_random = libtcod.random_new_from_seed(seed, algo=libtcod.RNG_CMWC)
        self.noise2d = libtcod.noise_new(2, random=self.my_random)

    def generate_block(self, idx=0, idy=0, map_size=256):
        """Block generation algorithm using simplex noise"""
        octaves = 8
        freq = 16.0 * octaves
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
                val = libtcod.noise_get_fbm(noise2d, [(idx * map_size + x) / freq,
                              (idy * map_size + y) / freq],
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

def generate_obstacle_map(tiles, map_size):
    """Generates map of tiles that are obstacles.
       Entities are added onto the map as they are generated"""
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

def generate_hidden_map(map_size):
    """Have to generate most of the map at draw runtime due to boundry issues"""
    # TODO generate, ignore boundry tiles. Update boundry tiles when block available
    return [[None for _ in range(map_size)] for _ in range(map_size)]
