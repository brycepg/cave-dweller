"""container for Block"""

import random
import logging

import libtcodpy as libtcod

from gen_map import generate_block

from game import Game
from tiles import Tiles
import entities
from util import get_neighbors

log = logging.getLogger(__name__)

class Block:
    """Segment of world populated by object and terrain"""
    def __init__(self, idx, idy, world, tiles=None, objects=None, load_turn=0):
        #print("init new block: {}x{}".format(idx, idy))
        if (idx, idy) in world.blocks:
            raise RuntimeError("Block already created")

        self.world = world
        self.idx = idx
        self.idy = idy
        self.load_turn = load_turn
        self.turn_delta = None
        #log.info("%dx%d load_turn: %d", self.idx, self.idy, load_turn)

        self.block_seed = self.world.rand_seed + (self.idx * 65565 + self.idy)

        if not tiles:
            self.tiles = []
            self.tiles = self.generate_tile_map()
        else:
            self.tiles = tiles
        if not objects:
            self.objects = []
            self.objects += self.generate_objects()
        else:
            self.objects = objects

    def generate_objects(self):
        """Generate object from generation table"""
        objects = []
        for monster, spawn_chance, amt in entities.generation_table:
            for _ in range(amt):
                if random.randint(0, 100) < spawn_chance:
                    x = random.randint(0, Game.map_size)
                    y = random.randint(0, Game.map_size)
                    if (not self.get_tile(x, y).is_obstacle and
                            not self.get_object(x, y)):
                        m = monster(x, y)
                        m.initial = True
                        objects.append(m)
        return objects

    def remove_object(self, a_object, x, y):
        """Remove object at location relative to block coordinates"""
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        entity = blk.objects.remove(a_object)
        return entity

    def set_object(self, a_class, x, y, kw_dict=None):
        """create an object from a_class at relative block location x,y.
           give keyword args to entity."""
        if kw_dict is None:
            kw_dict = {}
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        if not blk.get_tile(x, y).is_obstacle and not blk.get_object(x, y):
            a_obj = a_class(x, y, **kw_dict)
            blk.objects.append(a_obj)
            return a_obj
        else:
            return None

    def get_object(self, x, y):
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        # TODO put objects in their own array
        for a_obj in blk.objects:
            if a_obj.x == x and a_obj.y == y:
                return a_obj

        return None

    def get_abs(self, local_x, local_y):
        """Get absolute coordinate from local block coordiante"""
        abs_x = Game.map_size * self.idx + local_x
        abs_y = Game.map_size * self.idy + local_y
        return abs_x, abs_y

    def get_drawable_coordinate(self, local_x, local_y):
        """Get drawable coordinate from local block coordinate"""
        abs_x, abs_y = self.get_abs(local_x, local_y)
        draw_x = abs_x - Game.view_x
        draw_y = abs_y - Game.view_y
        return draw_x, draw_y

    def reposition_object(self, a_object):
        """Breadth first search for nearest non-obstacle to reposition object
        if's its stuck in an obstacle during generation"""

        if not self.get_tile(a_object.x, a_object.y).is_obstacle:
            return
        searched_list = [(a_object.x, a_object.y)]
        to_search = []
        neighbors = get_neighbors(a_object.x, a_object.y)

        while True:
            for neighbor in neighbors:
                # Do not search previously searched tiles
                if neighbor in searched_list:
                    continue

                # Exit condition --- ground open tile
                if not self.get_tile(*neighbor).is_obstacle:
                    a_object.x, a_object.y = neighbor
                    return
                else:
                    # Searched position but haven't
                    searched_list.append(neighbor)
                    # searched positions next to it
                    to_search.append(neighbor)

            # Use list like queue to to bfs search
            neighbors = get_neighbors(*to_search.pop(0))

    def reposition_objects(self):
        """Move objects until square is found that's not an obstacle"""
        for a_object in self.objects:
            self.reposition_object(a_object)

    def get_tile(self, x, y):
        """Get namedtuple of tile location, even if out of bounds."""
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            tile_id = self.tiles[y][x]
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            new_x = x % Game.map_size
            new_y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
            tile_id = blk.tiles[new_y][new_x]
        #print "tile: {}".format(tile)
        #print "tile lookup: {}".format(self.tile_lookup[tile])
        return Tiles.tile_lookup[tile_id]

    def set_tile(self, x, y, tile):
        """Set tile at location"""
        #print("tile :{}".format(tile))
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            self.tiles[y][x] = tile
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            new_x = x % Game.map_size
            new_y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
            blk.tiles[new_y][new_x] = tile

    def generate_tile_map(self):
        """Generate tiles from map function"""
        return generate_block(self.world.perlin_seed,
                              self.idx, self.idy,
                              map_size=Game.map_size)
    def process(self):
        """Do block calculations. Manage block objects update"""

        objects = self.objects
        idx = self.idx
        idy = self.idy
        map_size = Game.map_size

        for a_object in objects:
            if a_object.new_block_turn == self.world.turn:
                continue
            if not a_object.is_dead:
                a_object.process(self)
            else:
                a_object.decompose(self)


        # Reverse enumerate to allow removal of object
        for i, a_object in reversed(list(enumerate(objects))):
            if a_object.out_of_bounds():
                # Transfer object to new block-coordinate system
                idx_mod = a_object.x // map_size
                idy_mod = a_object.y // map_size
                a_object.x = a_object.x % map_size
                a_object.y = a_object.y % map_size
                new_block = self.world.get(idx + idx_mod,
                                           idy + idy_mod)
                a_object.new_block_turn = self.world.turn
                #log.debug("object crossed border at {} {}x{}".format(a_object,
                #                                        a_object.x,
                #                                        a_object.y))
                free_agent = objects.pop(i)
                new_block.objects.append(free_agent)

    def draw(self):
        """Draw block cells that are in frame"""
        self.draw_block()
        self.draw_objects()

    def draw_block(self):
        """ Draw block terrain.
        Call assumption: The block needs to be in the drawable area
        """
        #self.block_generator = libtcod.random_new_from_seed(self.block_seed)
        #block_generator = self.block_generator
        #random_get_int = libtcod.random_get_int

        map_size = Game.map_size
        min_x = Game.min_x
        max_x = Game.max_x
        min_y = Game.min_y
        max_y = Game.max_y

        idx = self.idx
        idy = self.idy

        view_x = Game.view_x
        view_y = Game.view_y
        game_con = Game.game_con

        get_tile = self.get_tile
        tiles = self.tiles
        tile_lookup = Tiles.tile_lookup

        # Figure out start, end location of tiles which need to be drawn
        # for this block
        block_abs_x_min = map_size * self.idx
        block_abs_y_min = map_size * self.idy

        block_abs_x_max = map_size * (self.idx+1) - 1
        block_abs_y_max = map_size * (self.idy+1) - 1

        draw_x_min_abs = max(block_abs_x_min, min_x)
        draw_y_min_abs = max(block_abs_y_min, min_y)
        draw_x_max_abs = min(block_abs_x_max, max_x)
        draw_y_max_abs = min(block_abs_y_max, max_y)

        loc_x_min = draw_x_min_abs % map_size
        loc_y_min = draw_y_min_abs % map_size

        loc_x_max = draw_x_max_abs % map_size
        loc_y_max = draw_y_max_abs % map_size

        # +1 makes bound inclusive
        for row in range(loc_y_min, loc_y_max+1):
            abs_y = map_size * idy + row
            for column in range(loc_x_min, loc_x_max+1):
                #tile_seed = random_get_int(block_generator, 0, 65565)
                abs_x = map_size * idx + column
                cur_tile = tile_lookup[tiles[row][column]]

                # TODO generate t/f array for hidden objects
                #print("{} {} {} {}".format(right, left, down, up))
                # Hide obstacles that are hidden by other hidden blocks
                if(get_tile(column+1, row).adjacent_hidden and
                   get_tile(column-1, row).adjacent_hidden and
                   get_tile(column, row+1).adjacent_hidden and
                   get_tile(column, row-1).adjacent_hidden):
                    draw_char = ' '
                    bg = Tiles.wall.bg
                    fg = None
                else:
                    draw_char = cur_tile.char
                    bg = cur_tile.bg
                    fg = cur_tile.fg

                if cur_tile.attributes:
                    chars = cur_tile.attributes.get('alternative_characters')
                    if chars:
                        char_choice = 2
                        if char_choice != len(chars):
                            draw_char = chars[char_choice]
                        else:
                            draw_char = cur_tile.char

                libtcod.console_put_char_ex(game_con,
                        abs_x - view_x,
                        abs_y - view_y,
                        draw_char, fg, bg)

    def draw_objects(self):
        """Put block's drawable objects on game con"""
        for a_object in self.objects:
            abs_x = int(Game.map_size * self.idx + a_object.x)
            abs_y = int(Game.map_size * self.idy + a_object.y)
            if Game.in_drawable_coordinates(abs_x, abs_y):

                # Use tile's background if object doesn't set it
                cur_bg = a_object.bg
                if cur_bg is None:
                    cur_bg = self.get_tile(int(a_object.x), int(a_object.y)).bg

                libtcod.console_put_char_ex(Game.game_con,
                     (abs_x - Game.view_x),
                     (abs_y - Game.view_y),
                     a_object.char, a_object.fg, cur_bg)
