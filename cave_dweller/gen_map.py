#!/usr/bin/env python3

import random

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
    for x in size:
        y_line = []
        append = y_line.append
        for y in size:
            val = snoise2((idx * map_size + x) / freq,
                          (idy * map_size + y) / freq,
                          octaves, base=seed,
                          repeatx=65536,
                          repeaty=65536)
            if val < 0 and val > -.2:
                out = random.choice(Id.any_ground)
            else:
                out = 255
            append(out)
        append_blk(y_line)
    return block

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
    return [[None for _ in range(map_size)] for _ in range(map_size)]
