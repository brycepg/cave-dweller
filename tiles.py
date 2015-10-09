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
    ['char', 'is_obstacle', 'fg', 'bg', 'adjacent_hidden', 'diggable', 'buildable', 'attributes']
)
Tile.__new__.__defaults__ = \
    (' ',    False,    libtcod.black, None, False,          False,     False,        None)

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
    ground  = Tile('-', is_obstacle=False, fg=gray, bg=ground_bg, buildable=True, attributes={'build': [Id.build1]})
    ground2 = Tile('.', is_obstacle=False, fg=gray, bg=ground_bg, buildable=True, attributes={'build': [Id.build1]})
    ground3 = Tile('`', is_obstacle=False, fg=gray, bg=ground_bg, buildable=True, attributes={'build': [Id.build1]})

    wall = Tile('x', is_obstacle=True, fg=white, bg=wall_bg, adjacent_hidden=True, diggable=True, attributes={'dig': [Id.dig1]})

    build1 = Tile(char=176, is_obstacle=False, fg=wall_bg, bg=ground_bg, buildable=True,  diggable=True, attributes={'build': [Id.build2], 'dig': Id.any_ground})
    build2 = Tile(char=177, is_obstacle=False, fg=wall_bg, bg=ground_bg, buildable=True,  diggable=True, attributes={'build': [Id.build3], 'dig': [Id.build1]})
    build3 = Tile(char=178, is_obstacle=False, fg=wall_bg, bg=ground_bg, buildable=True,  diggable=True, attributes={'build': [Id.wall],   'dig': [Id.build2]})

    dig1 = Tile(char=178, is_obstacle=True, fg=wall_bg, bg=ground_bg, adjacent_hidden=True, buildable=True, diggable=True, attributes={'dig': [Id.dig2], 'build': [Id.wall]})
    dig2 = Tile(char=177, is_obstacle=True, fg=wall_bg, bg=ground_bg, adjacent_hidden=True, buildable=True, diggable=True, attributes={'dig': [Id.dig3], 'build': [Id.dig1]})
    dig3 = Tile(char=176, is_obstacle=True, fg=wall_bg, bg=ground_bg, adjacent_hidden=True, buildable=True, diggable=True, attributes={'dig': Id.any_ground, 'build': [Id.dig2]})

    null = Tile(is_obstacle=True, fg=red, bg=red)

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
