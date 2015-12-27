import timeit
import random

map_size = 96

# with_mod .06 uS slower

def calc_coord_with_mod(abs_x, abs_y):
    idx = abs_x // map_size
    idy = abs_y // map_size
    local_x = abs_x % map_size
    local_y = abs_y % map_size
    return (idx, idy), (local_x, local_y)

def calc_coord_without(abs_x, abs_y):
    idx = abs_x // map_size
    idy = abs_y // map_size
    local_x = abs_x - (map_size * idx)
    local_y = abs_y - (map_size * idy)
    return (idx, idy), (local_x, local_y)

def divmod_comparison(abs_x, abs_y):
    return divmod(abs_x, map_size), divmod(abs_y, map_size)
