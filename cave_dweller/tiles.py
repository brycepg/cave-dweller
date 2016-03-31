"""Collection of nametuples defining attributes for game tiles, and ids which
reference those attributes in a lookup table
"""
import colors
from collections import namedtuple

ground_bg = colors.darkest_gray
ground_fg = colors.gray

wall_bg = colors.gray
wall_fg = colors.white

# pylint: disable=dangerous-default-value
# This pylint thinks color reference is 'dangerous' because it is an object.
# It is not
Tile = namedtuple('Tile',
    ['char', 'is_obstacle', 'fg', 'bg', 'adjacent_hidden', 'diggable', 'buildable', 'attributes', 'name']
)
Tile.__new__.__defaults__ = \
    (' ',    False,    colors.black, None, False,          False,     False,        None,         None)

class Id(object):
    """Defines all the tile ids -- block.tiles vlaues"""
    ground, ground2, ground3 = [0, 1, 2]

    build1, build2, build3 = [249, 250, 251]
    dig1, dig2, dig3 = [252, 253, 254]
    wall = 255

    any_ground = [ground, ground2, ground3]

class Tiles(object):
    """Defines all the tiles."""
    #TODO: offload to configuration files

    # Permutation of characters
    ground  = Tile(ord('-'), is_obstacle=False, fg=ground_fg, bg=ground_bg, buildable=True, attributes={'build': [Id.build1]}, name="Ground")
    ground2 = Tile(ord('.'), is_obstacle=False, fg=ground_fg, bg=ground_bg, buildable=True, attributes={'build': [Id.build1]}, name="Ground")
    ground3 = Tile(ord('`'), is_obstacle=False, fg=ground_fg, bg=ground_bg, buildable=True, attributes={'build': [Id.build1]}, name="Ground")

    wall = Tile(ord('x'), is_obstacle=True, fg=wall_fg, bg=wall_bg, adjacent_hidden=True, diggable=True, attributes={'dig': [Id.dig1]}, name="Limestone")

    build1 = Tile(char=176, is_obstacle=False, fg=wall_bg, bg=ground_bg, buildable=True,  diggable=True, attributes={'build': [Id.build2], 'dig': Id.any_ground})
    build2 = Tile(char=177, is_obstacle=False, fg=wall_bg, bg=ground_bg, buildable=True,  diggable=True, attributes={'build': [Id.build3], 'dig': [Id.build1]})
    build3 = Tile(char=178, is_obstacle=False, fg=wall_bg, bg=ground_bg, buildable=True,  diggable=True, attributes={'build': [Id.wall],   'dig': [Id.build2]})

    dig1 = Tile(char=178, is_obstacle=True, fg=wall_bg, bg=ground_bg, adjacent_hidden=True, buildable=True, diggable=True, attributes={'dig': [Id.dig2], 'build': [Id.wall]})
    dig2 = Tile(char=177, is_obstacle=True, fg=wall_bg, bg=ground_bg, adjacent_hidden=True, buildable=True, diggable=True, attributes={'dig': [Id.dig3], 'build': [Id.dig1]})
    dig3 = Tile(char=176, is_obstacle=True, fg=wall_bg, bg=ground_bg, adjacent_hidden=True, buildable=True, diggable=True, attributes={'dig': Id.any_ground, 'build': [Id.dig2]})

    null = Tile(is_obstacle=True, fg=colors.red, bg=colors.red)

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
