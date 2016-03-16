import sys
import random

import numpy as np

sys.path.append("../cave_dweller")
sys.path.append("cave_dweller")
import gen_map

my_maps = [gen_map.generate_block(random.randint(-100, 100)) for _ in range(3)]

np_maps = [np.array(a_map) for a_map in my_maps]

def access_np():
    loc_np_maps = np_maps
    for a_map in loc_np_maps:
        for y in range(len(a_map)):
            for x in range(len(a_map)):
                print(a_map[y][x])

def access_2dl():
    loc_my_maps = my_maps
    for a_map in loc_my_maps:
        for row in a_map:
            for x in row:
                print(row[x])

# 2dl is just as fast
