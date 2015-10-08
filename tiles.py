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
     'buildable',
     'attributes']
)

class Id(object):
    """Defines all the tile ids -- block.tiles vlaues"""
    ground, ground2, ground3 = [0, 1, 2]

    build1, build2, build3 = [249, 250, 251]
    dig1, dig2, dig3 = [252, 253, 254]
    wall = 255

    any_ground = [ground, ground2, ground3]

class Tiles:
    """Defines all the tiles."""
    #TODO: offload to configuration files

    # Permutation of characters
    ground = Tile('-', False, gray, ground_bg, False, False, True, {'build': [Id.build1]})
    ground2 = Tile('.', False, gray, ground_bg, False, False, True, {'build': [Id.build1]})
    ground3 = Tile('`', False, gray, ground_bg, False, False, True, {'build': [Id.build1]})

    wall = Tile('x', True, white, wall_bg, True, True, False, {'dig': [Id.dig1]})

    build1 = Tile(176, False, wall_bg, ground_bg, False, True, True, {'build': [Id.build2], 'dig': Id.any_ground})
    build2 = Tile(177, False, wall_bg, ground_bg, False, True, True, {'build': [Id.build3], 'dig': [Id.build1]})
    build3 = Tile(178, False, wall_bg, ground_bg, False, True, True, {'build': [Id.wall], 'dig': [Id.build2]})

    dig1 = Tile(178, True, wall_bg, ground_bg, True, True, True, {'dig': [Id.dig2], 'build': [Id.wall]})
    dig2 = Tile(177, True, wall_bg, ground_bg, True, True, True, {'dig': [Id.dig3], 'build': [Id.dig1]})
    dig3 = Tile(176, True, wall_bg, ground_bg, True, True, True, {'dig': Id.any_ground, 'build': [Id.dig2]})

    null = Tile(' ', True, red, red, False, False, False, None)

    # Map stores array of tiles -- map tile id to nameduple
    tile_lookup = {
        Id.ground: ground,
        Id.ground2: ground2,
        Id.ground3: ground3,
        Id.build1: build1,
        Id.build2: build2,
        Id.build3: build3,
        Id.dig1: dig1,
        Id.dig2: dig2,
        Id.dig3: dig3,
        Id.wall: wall,
        None: null,
    }
