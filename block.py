"""container for Block"""

import math
import time
from collections import namedtuple

import libtcodpy as libtcod

from gen_map import generate_map_slice
from gen_map import generate_map_slice_abs_min
from gen_map import generate_map_slice_abs_more
from game import Game

white = libtcod.white
black = libtcod.black
gray = libtcod.gray
red = libtcod.red

Tile = namedtuple('Tile', ['char', 'is_obstacle', 'fg', 'bg', 'adjacent_hidden'])

wall = Tile('x', True, white, gray, True)
ground = Tile('-', False, gray, black, False)
null = Tile(' ', True, red, red, False)


class Block:


    """Segment of world populated by object and terrain"""
    def __init__(self, idx, idy, world):
        self.tile_lookup = {
            0: ground,
            255: wall,
            None: null,
        }
        #self.delay_generation = False if len(world.blocks) <= 1 else True
        self.delay_generation = False
        self.world = world
        self.tiles = []
        self.objects = []
        self.idx = idx
        self.idy = idy

        self.completely_generated = False
        self.y_coord_gen_num = 0
        self.init_map_slices()

    def neighbors(self, x, y):
        """Get taxicab neighbors(4-way) from coordinates"""
        return [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]

    def reposition_object(self, a_object):
        """Breadth first search for nearest non-obstacle"""

        print(self.get_tile(a_object.x, a_object.y, True))

        if not self.get_tile(a_object.x,a_object.y, True).is_obstacle:
            return
        searched_list=[(a_object.x, a_object.y)]
        to_search=[]
        neighbors = self.neighbors(a_object.x, a_object.y)
        while True:
            for neighbor in neighbors:
                if Game.show_algorithm:
                    time.sleep(.01)
                    Game.win.putchar('O', neighbor[0], neighbor[1], 'red')
                    Game.win.update()
                    print(neighbor)
                if neighbor in searched_list:
                    continue
                if not self.get_tile(*neighbor, generate_new_blocks=True).is_obstacle:
                    a_object.x, a_object.y = neighbor
                    return
                else:
                    searched_list.append(neighbor)
                    to_search.append(neighbor)
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

    def get_tile(self, x, y, generate_new_blocks=False):
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


    def init_map_slices(self):
        """Generate block in 'slices' to allow a
            'timeout' after a certain threshold
             To allow other parts of the game to update."""
        perlin_seed = self.world.perlin_seed
        idx = self.idx
        idy = self.idy
        map_size = Game.map_size
        tiles = self.tiles

        while not Game.past_loop_time() or not self.delay_generation:
            #print(self.world.perlin_seed)
            num_map_slice = generate_map_slice_abs_more(perlin_seed,
                                                        idx,
                                                        idy,
                                                        self.y_coord_gen_num,
                                                        map_size=map_size)
            tiles.append(num_map_slice)
            self.y_coord_gen_num += 1
            if self.y_coord_gen_num >= Game.map_size:
                self.completely_generated = True
                break
        if Game.past_loop_time():
            print("past_time")
    def process(self):
        """Do block calculations. Manage block objects update"""
        if not self.completely_generated:
            self.init_map_slices()
            return

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
#               if a_object.x >= Game.map_size:
#                   new_block = Block(self.idx+1, self.idy, self.world)
#                   a_object.x = a_object.x % Game.map_size
#               elif a_object.x < 0:
#                   new_block = Block(self.idx-1, self.idy, self.world)
#                   a_object.x = Game.map_size + a_object.x
#               elif a_object.y >= Game.map_size:
#                   new_block = Block(self.idx, self.idy+1, self.world)
#                   a_object.y = a_object.y % Game.map_size
#               elif a_object.y < 0:
#                   new_block = Block(self.idx, self.idy-1, self.world)
#                   a_object.y = Game.map_size + a_object.y
                print("a_object {} {}x{}".format(a_object, a_object.x, a_object.y))
                free_agent = objects.pop(i)
                new_block.objects.append(free_agent)
                new_blocks.append(new_block)

        return new_blocks

    def draw(self):
        """Draw block cells that are in frame"""
        if not self.completely_generated:
            return
        self.draw_block()
        self.draw_objects()

    def draw_block(self):
        """Draw block terrain"""

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
                abs_x = map_size * idx + column
                if((min_x <= abs_x <= max_x) and
                   (min_y <= abs_y <= max_y)):

                    cur_tile = tile_lookup[tiles[row][column]]
                    draw_char = cur_tile.char

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
                    libtcod.console_put_char_ex(0,
                            abs_x - center_x + screen_width//2,
                            abs_y - center_y + screen_height//2,
                            draw_char, cur_tile.fg, cur_tile.bg)
    def draw_objects(self):
        """Put block's drawable objects on screen"""
        for a_object in self.objects:
            abs_x = int(Game.map_size * self.idx + a_object.x)
            abs_y = int(Game.map_size * self.idy + a_object.y)
            if Game.in_drawable_coordinates(abs_x, abs_y):

                # Use tile's background if object doesn't set it
                cur_bg = a_object.bg
                if cur_bg is None:
                    cur_bg = self.get_tile(a_object.x, a_object.y).bg

                libtcod.console_put_char_ex(0,
                     (abs_x - Game.center_x + Game.screen_width//2),
                     (abs_y - Game.center_y + Game.screen_height//2),
                     a_object.char, a_object.fg, cur_bg)
