#!/usr/bin/env python3

import sys
import time
import random
import os

from noise import snoise2
from tiles import Id

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
                out = 255 if x==0 else 0
                pgm_out.write("%s\n" % out)


def generate_map_slice(seed, idx, idy, y, map_size=256):
    """
    Generate one y-slice of a block
    To string generation over many game loops
    NOTE: stored in row-major format
    """
    octaves = 8
    freq = 16.0 * octaves
    row_line = []
    for x_cell in range(map_size):
        val = snoise2((idx * map_size + x_cell) / freq,
                            (idy * map_size + y) / freq, 
                            octaves, base=seed,                                      
                            repeatx = 65536,
                            repeaty = 65536)
        if val < 0:
            out=0
        else:
            out=255
        row_line.append(out)
    return row_line


def generate_map(seed, idx=0, idy=0, map_size=256, func=generate_map_slice):
    block = []
    for y in range(map_size):
        x_line = func(seed, idx, idy, y, map_size)
        block.append(x_line)
    return block


def generate_map_slice_abs_min(seed, idx, idy, y, map_size=256):
    """
    """
    octaves = 8
    freq = 16.0 * octaves
    row_line = []
    for x_cell in range(map_size):
        val = snoise2((idx * map_size + x_cell) / freq,
                            (idy * map_size + y) / freq, 
                            octaves, base=seed,                                      
                            repeatx = 65536,
                            repeaty = 65536)
        if abs(val) < 0.055:
            out=0
        else:
            out=255
        row_line.append(out)
    return row_line


def generate_map_slice_abs_more(seed, idx, idy, y, map_size=256):
    """
    """
    octaves = 8
    freq = 16.0 * octaves
    row_line = []
    for x_cell in range(map_size):
        val = snoise2((idx * map_size + x_cell) / freq,
                            (idy * map_size + y) / freq, 
                            octaves, base=seed,                                      
                            repeatx = 65536,
                            repeaty = 65536)
        if val < 0 and val > -.2:
            out=0
        else:
            out=255
        row_line.append(out)
    return row_line

if __name__ == "__main__":
    import argparse
    block = generate_map(0,0,0, func=generate_map_slice)
    write_map(block, path="reg.pgm")
    block = generate_map(0,0,0, func=generate_map_slice_abs_min)
    write_map(block, path="abs_min.pgm")
    block = generate_map(0,0,0, func=generate_map_slice_abs_more)
    write_map(block, path="abs_more.pgm")


def generate_map_whole(seed, idx=0, idy=0, map_size=256):
    octaves = 8
    freq = 16.0 * octaves
    block = []
    for y in range(map_size):
        x_line = []
        append = x_line.append
        for x_cell in range(map_size):
            val = snoise2((idx * map_size + x_cell) / freq,
                                (idy * map_size + y) / freq, 
                                octaves, base=seed,                                      
                                repeatx = 65536,
                                repeaty = 65536)
            if val < 0 and val > -.2:
                out = random.choice(Id.any_ground)
            else:
                out = 255
            append(out)
        block.append(x_line)
    return block
#    #block = []
#    octaves = 8
#    freq = 16.0 * octaves
#    vals = [ _ for _ in range(map_size) ]
#    block_noise = [ [snoise2((idx * map_size + x) / freq, idy * map_size + y, octaves, base=seed, repeatx = 65536, repeaty = 65536) for x in vals] for y in vals]
#    block = [ [0 if val < 0 else 255 for val in line] for line in block_noise ]
#    return block
