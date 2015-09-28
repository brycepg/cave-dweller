#!/usr/bin/env python3

import sys
import time
import random

from noise import snoise2

def write_map(block, idx, idy, name=None):
    """Write map to file in pgm format"""
    if not name:
        pgm_out_name = ''.join['map_', str(idx), 'x', str(idy), '.pgm']
    with open(pgm_out_name, 'wt') as pgm_out:
        pgm_out.write('P2\n')
        pgm_out.write('{blksz} {blksz}\n'.format(blksz=len(block)))
        pgm_out.write('255\n')
        for x in block:
            for y in block:
                char = block[x][y]
                if char == 'x':
                    out = 255
                elif char == '.':
                    out = 0
                pgm_out.write("%s\n" % out)

def generate_map_slice(seed, idx, idy, y, map_size=256):
    """
    Generate one y-slice of a block
    To string generation over many game loops
    NOTE: stored in row major format
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
        #print(val)
        if val < 0:
            out=0
        else:
            out=255
        row_line.append(out)
    return row_line

def generate_map(seed, idx=0, idy=0, map_size=256):
    block = []
    for y in range(map_size):
        x_line = generate_map_slice(seed, idx, idy, y, map_size)
        block.append(x_line)
    return block
