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


def generate_block(seed, idx=0, idy=0, map_size=256):
    octaves = 8
    freq = 16.0 * octaves
    block = []
    size = range(map_size)
    append_blk = block.append
    for y in size:
        x_line = []
        append = x_line.append
        for x_cell in size:
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
        append_blk(x_line)
    return block
