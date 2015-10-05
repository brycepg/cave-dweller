from collections import namedtuple
import random

#from util import classproperty

import libtcodpy as libtcod

white = libtcod.white
black = libtcod.black
gray = libtcod.gray
red = libtcod.red

ground_bg = libtcod.darkest_gray
wall_bg = gray

Tile = namedtuple('Tile', 
    ['char',
     'is_obstacle',
     'fg',
     'bg',
     'adjacent_hidden',
     'diggable',
     'attributes']
)

class Id(object):
    """Defines all the tile ids -- block.tiles vlaues"""
    ground = 0
    ground2 = 1
    ground3 = 2
    dig1 = 3
    dig2 = 4
    dig3 = 5
    wall = 255

    any_ground = [ground, ground2, ground3]

class Tiles:
    """Defines all the tiles."""
    #TODO: offload to configuration files
    ground = Tile('-', False, gray, ground_bg, False, False, None)
    ground2 = Tile('.', False, gray, ground_bg, False, False, None)
    ground3 = Tile('`', False, gray, ground_bg, False, False, None)

    wall = Tile('x', True, white, wall_bg, True, True, {'next': Id.dig1})

    dig1 = Tile(178, True, wall_bg, ground_bg, True, True, {'next': Id.dig2})
    dig2 = Tile(177, True, wall_bg, ground_bg, True, True, {'next': Id.dig3})
    dig3 = Tile(176, True, wall_bg, ground_bg, True, True, {'next': Id.ground})

    null = Tile(' ', True, red, red, False, False, None)

    tile_lookup = {
        Id.ground: ground,
        Id.ground2: ground2,
        Id.ground3: ground3,
        Id.dig1: dig1,
        Id.dig2: dig2,
        Id.dig3: dig3,
        Id.wall: wall,
        None: null,
    }
