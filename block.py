"""container for Block"""

import math
import time
from collections import namedtuple
import random

import libtcodpy as libtcod

from gen_map import generate_map_whole

from game import Game

white = libtcod.white
black = libtcod.black
gray = libtcod.gray
red = libtcod.red

Tile = namedtuple('Tile', ['char', 'is_obstacle', 'fg', 'bg', 'adjacent_hidden', 'attributes'])

wall = Tile('x', True, white, gray, True, None)
ground = Tile('-', False, gray, libtcod.darkest_gray, False, {'alternative_characters': [',', '\'']})
ground2 = Tile('.', False, gray, libtcod.darkest_gray, False, None)
ground3 = Tile('`', False, gray, libtcod.darkest_gray, False, None)
null = Tile(' ', True, red, red, False, None)


class Block:
    """Segment of world populated by object and terrain"""
    def __init__(self, idx, idy, world):
        self.tile_lookup = {
            0: ground,
            1: ground2,
            2: ground3,
            255: wall,
            None: null,
        }
        self.world = world
        self.tiles = []
        self.objects = []
        self.idx = idx
        self.idy = idy

        self.block_seed = self.world.rand_seed + (self.idx * 65565 + self.idy)
        #self.block_generator = libtcod.random_new_from_seed(self.block_seed)
        #print("block seed: %d" % self.block_seed)

        self.tiles = self.generate_tile_map()

    def neighbors(self, x, y):
        """Get taxicab neighbors(4-way) from coordinates"""
        return [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]

    def get_abs(self, local_x, local_y):
        """Get absolute coordinate from local block coordiante"""
        abs_x = Game.map_size * self.idx + local_x
        abs_y = Game.map_size * self.idy + local_y
        return abs_x, abs_y

    def get_drawable_coordinate(self, local_x, local_y):
        """Get drawable coordinate from local block coordinate"""
        abs_x, abs_y = self.get_abs(local_x, local_y)
        draw_x = abs_x - Game.center_x + Game.screen_width//2
        draw_y = abs_y - Game.center_y + Game.screen_height//2
        return draw_x, draw_y

    def reposition_object(self, a_object):
        """Breadth first search for nearest non-obstacle to reposition object
        if's its stuck in an obstacle during generation"""

        if not self.get_tile(a_object.x,a_object.y, True).is_obstacle:
            return
        searched_list = [(a_object.x, a_object.y)]
        to_search = []
        neighbors = self.neighbors(a_object.x, a_object.y)

        # Visualization for debugging/coolness
        if Game.show_algorithm:
            draw_x, draw_y = self.get_drawable_coordinate(a_object.x, a_object.y)
            libtcod.console_set_char_background(0, draw_x, draw_y, libtcod.red)

        while True:
            for neighbor in neighbors:
                # Do not search previously searched tiles
                if neighbor in searched_list:
                    continue

                # Visualization for debugging/coolness
                if Game.show_algorithm:
                    abs_y = Game.map_size * self.idy + neighbor[1]
                    abs_x = Game.map_size * self.idx + neighbor[0]
                    libtcod.console_put_char_ex(0, 
                            abs_x - Game.center_x + Game.screen_width//2,
                            abs_y - Game.center_y + Game.screen_height//2,
                            ' ', libtcod.red, libtcod.red)
                    libtcod.console_flush()
                    print(neighbor)

                # Exit condition --- ground open tile
                if not self.get_tile(*neighbor, generate_new_blocks=True).is_obstacle:
                    a_object.x, a_object.y = neighbor
                    return
                else:
                    # Searched position but haven't 
                    searched_list.append(neighbor)
                    # searched positions next to it
                    to_search.append(neighbor)

            # Use list like queue to to bfs search
            neighbors = self.neighbors(*to_search.pop(0))
        
    def reposition_objects(self):
        """Move objects until square is found that's not an obstacle"""
        for a_object in self.objects:
            self.reposition_object(a_object)

    def within_bounds(self, x, y):
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            return True
        else:
            return False

    def get_tile(self, x, y, generate_new_blocks=True):
        """"Get namedtuple of tile location, even if out of bounds.
        Note: This is not merged into get_tile_id because of performance
        ~10fps increase by not calling get_tile_id"""
        tile = None
        blk = None
        if self.within_bounds(x, y):
            return self.tile_lookup[self.tiles[y][x]]
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            if generate_new_blocks:
                blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
            else:
                try:
                    blk = self.world.blocks[(self.idx + idx_mod, self.idy + idy_mod)]
                except KeyError:
                    pass
            if blk is not None:
                new_x = x % Game.map_size
                new_y = y % Game.map_size
                tile = blk.tiles[new_y][new_x]
        #print "tile: {}".format(tile)
        #print "tile lookup: {}".format(self.tile_lookup[tile])
        return self.tile_lookup[tile]

    def get_tile_id(self, x, y, generate_new_blocks=False):
        """Get id of tile, even if outside of blocks bounds."""
        tile = None
        blk = None
        if self.within_bounds(x, y):
            return self.tiles[y][x]
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            if generate_new_blocks:
                blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
            else:
                try:
                    blk = self.world.blocks[(self.idx + idx_mod, self.idy + idy_mod)]
                except KeyError:
                    pass
            if blk is not None:
                new_x = x % Game.map_size
                new_y = y % Game.map_size
                tile = blk.tiles[new_y][new_x]
            return tile


    def generate_tile_map(self):
        """Generate tiles from map function"""
        return generate_map_whole(self.world.perlin_seed,
                                  self.idx, self.idy,
                                  map_size=Game.map_size)
    def process(self):
        """Do block calculations. Manage block objects update"""

        new_blocks = []
        objects = self.objects
        idx = self.idx
        idy = self.idy
        map_size = Game.map_size
        world = self.world

        for a_object in objects:
            a_object.move(self)

        for i, a_object in reversed(list(enumerate(objects))):
            if a_object.out_of_bounds():
                # Transfer object to new block-coordinate system
                new_block = Block(idx+ (a_object.x//map_size), idy + (a_object.y//map_size), world)
                a_object.x = a_object.x % map_size
                a_object.y = a_object.y % map_size
                print("a_object {} {}x{}".format(a_object, a_object.x, a_object.y))
                free_agent = objects.pop(i)
                new_block.objects.append(free_agent)
                new_blocks.append(new_block)

        return new_blocks

    def draw(self):
        """Draw block cells that are in frame"""
        self.draw_block()
        self.draw_objects()

    def draw_block(self):
        """Draw block terrain"""
        #self.block_generator = libtcod.random_new_from_seed(self.block_seed)
        #block_generator = self.block_generator
        #random_get_int = libtcod.random_get_int

        map_size = Game.map_size
        min_x = Game.min_x
        max_x = Game.max_x
        min_y = Game.min_y
        max_y = Game.max_y
        screen_width = Game.screen_width
        screen_height = Game.screen_height

        idx = self.idx
        idy = self.idy

        center_x = Game.center_x
        center_y = Game.center_y

        get_tile = self.get_tile
        tiles = self.tiles
        tile_lookup = self.tile_lookup

        for row in range(map_size):
            abs_y = map_size * idy + row
            for column in range(map_size):
                #tile_seed = random_get_int(block_generator, 0, 65565)
                abs_x = map_size * idx + column
                if((min_x <= abs_x <= max_x) and
                   (min_y <= abs_y <= max_y)):

                    cur_tile = tile_lookup[tiles[row][column]]
                    draw_char = cur_tile.char
                    bg = cur_tile.bg

                    if cur_tile.is_obstacle:
                        right = get_tile(column+1, row)
                        left = get_tile(column-1, row)
                        down = get_tile(column, row+1)
                        up = get_tile(column, row-1)
                        #print("{} {} {} {}".format(right, left, down, up))
                        if(up.adjacent_hidden and
                           down.adjacent_hidden and
                           left.adjacent_hidden and
                           right.adjacent_hidden):
                            draw_char = ' '
                            bg = wall.bg
                            

                    if cur_tile.attributes:
                        chars = cur_tile.attributes.get('alternative_characters')
                        if chars:
                            #char_choice = (self.world.perlin_seed * row + self.block_seed * column) % (len(chars)+1)
                            #char_choice = random.randint(0, len(chars))
                            #char_choice = libtcod.random_get_int(self.block_generator, 0, len(chars))
                            #char_choice = (((self.block_seed*column) % (row*self.world.perlin_seed+1)) + (self.block_seed % (self.world.rand_seed*column+1))) % (len(chars)+1)
                            char_choice = 2#tile_seed % (len(chars) + 1)
                            if char_choice != len(chars):
                                draw_char = chars[char_choice]
                            else:
                                draw_char = cur_tile.char

                    libtcod.console_put_char_ex(0,
                            abs_x - center_x + screen_width//2,
                            abs_y - center_y + screen_height//2,
                            draw_char, cur_tile.fg, bg)
    def draw_objects(self):
        """Put block's drawable objects on screen"""
        for a_object in self.objects:
            abs_x = int(Game.map_size * self.idx + a_object.x)
            abs_y = int(Game.map_size * self.idy + a_object.y)
            if Game.in_drawable_coordinates(abs_x, abs_y):

                # Use tile's background if object doesn't set it
                cur_bg = a_object.bg
                if cur_bg is None:
                    cur_bg = self.get_tile(int(a_object.x), int(a_object.y)).bg

                libtcod.console_put_char_ex(0,
                     (abs_x - Game.center_x + Game.screen_width//2),
                     (abs_y - Game.center_y + Game.screen_height//2),
                     a_object.char, a_object.fg, cur_bg)
