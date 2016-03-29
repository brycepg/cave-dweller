"""container for Block"""

import random
import logging
import operator
import itertools
from collections import deque

import libtcodpy as libtcod
from libtcodpy import _lib
put_char_ex = _lib.TCOD_console_put_char_ex

import hidden_map_handler
import entities
from game import Game
from tiles import Tiles
import gen_map
from gen_map import generate_block
from gen_map import generate_obstacle_map
from util import get_neighbors

log = logging.getLogger(__name__)
wall_bg = Tiles.wall.bg

class Block(object):
    """Segment of world populated by object and terrain"""
    def __init__(self, idx, idy, world, tiles=None, entities=None,
                 obstacle_map=None, hidden_map=None, load_turn=0):
        #print("init new block: {}x{}".format(idx, idy))
        if (idx, idy) in world.blocks:
            raise DuplicateBlockError("Block already created", idx, idy)

        self.world = world
        self.idx = idx
        self.idy = idy
        self.load_turn = load_turn
        self.save_turn = None

        # Could be used in the future to determine update need of block
        self.turn_delta = None

        # Not used yet. Maybe for block specific features?
        # Probably better to seed a generator for the block using this seed
        self.block_seed = self.world.seed_int + (self.idx * 1073741823 + self.idy)

        if not tiles:
            self.tiles = []
            self.tiles = self.generate_tile_map()
        else:
            self.tiles = tiles

        if not obstacle_map:
            self.obstacle_map = generate_obstacle_map(self.tiles,
                                                      Game.map_size)
        else:
            self.obstacle_map = obstacle_map

        if not entities:
            self.entity_list = []
            self.entities = gen_map.gen_empty_entities(Game.map_size)
            self.generate_entities()
        else:
            self.entities = entities
            self.entity_list = self.list_entities(entities)

        if not hidden_map:
            self.hidden_map = hidden_map_handler.generate_map(Game.map_size)
        else:
            self.hidden_map = hidden_map

    def is_obstacle(self, x, y):
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        return blk.obstacle_map[x][y]

    def __eq__(self, block):
        """
        Convenient equality for blocks

        Might not be a good idea for all the object references

        `=` now tests for contents
        `is` tests for id
        """
        return self.__dict__ == block.__dict__

    def list_entities(self, entities):
        entity_list = []
        for a_slice in entities:
            for a_tile in a_slice:
                for a_entity in a_tile:
                    entity_list.append(a_entity)
        return entity_list

    def generate_entities(self):
        """Generate object from generation table"""
        for monster, spawn_chance, amt in entities.generation_table:
            for _ in range(amt):
                if random.randint(0, 100) < spawn_chance:
                    # Randint is inclusive
                    x = random.randint(0, Game.map_size-1)
                    y = random.randint(0, Game.map_size-1)
                    if not self.is_obstacle(x, y):
                        m = self.set_entity(monster, x, y)
                        # Used for some monster's generation
                        m.initial = True

    def remove_entity(self, a_entity, x, y):
        """
        Remove object at location relative to block coordinates

        arguments
            a_entity - entity to remove
            x - block relative x coordinate
            y - block relative y coordinate

        raises ValueError if no entity at location
        """
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        if a_entity.is_obstacle:
            blk.obstacle_map[x][y] = False
        blk.entities[x][y].remove(a_entity)
        blk.entity_list.remove(a_entity)

    def set_entity(self, a_class, x, y, kw_dict=None):
        """create an object from a_class at relative block location x,y.
           give keyword args to entity.

           Does not do obstacle checking for tiles
           """
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

        a_entity = a_class(x, y, **kw_dict)
        if a_entity.is_obstacle:
            blk.obstacle_map[x][y] = True
        blk.entities[x][y].append(a_entity)
        blk.entity_list.append(a_entity)
        a_entity.cur_block = blk
        return a_entity

    def get_entity(self, x, y):
        """
        return top entity at x, y

        Raises IndexError if no entities at location(use get_entities instead)
        """
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        loc = blk.entities[x][y]
        if loc:
            return loc[-1]
        else:
            return None

    def get_entities(self, x, y):
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        return blk.entities[x][y]

    def move_entity(self, entity, new_x, new_y):
        """Move entity to correct position

        Does not check obstacle map
        """

        #log.info("call block %dx%d move entity %r at %dx%d to %dx%d", self.idx, self.idy, entity, entity.x, entity.y, new_x, new_y)

        if 0 <= new_x < Game.map_size and 0 <= new_y < Game.map_size:
            blk = self
        else:
            idx_mod = new_x // Game.map_size
            idy_mod = new_y // Game.map_size
            new_x = new_x % Game.map_size
            new_y = new_y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

            entity.cur_block = blk
            self.entity_list.remove(entity)
            blk.entity_list.append(entity)

        # Entities can start on obstacle(i.e. repostion entities)
        if not self.get_tile(entity.x,entity.y).is_obstacle:
            self.obstacle_map[entity.x][entity.y] = False
        self.entities[entity.x][entity.y].remove(entity)
        entity.x = new_x
        entity.y = new_y
        blk.entities[entity.x][entity.y].append(entity)
        if entity.is_obstacle:
            blk.obstacle_map[entity.x][entity.y] = True
        # Use return block to know where the object is
        return blk

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

    def reposition_entity(self, a_entity, avoid_hidden=False):
        """Breadth first search for nearest non-obstacle to reposition object
        if's its stuck in an obstacle during generation

        TODO FIX (move determine what's hidden out of draw)
        avoid hidden
            also do not reposition entity into hidden tiles"""

        if not self.get_tile(a_entity.x, a_entity.y).is_obstacle:
            return
        searched_list = [(a_entity.x, a_entity.y)]
        to_search = deque()
        neighbors = get_neighbors(a_entity.x, a_entity.y)

        while True:
            for neighbor in neighbors:
                # Do not search previously searched tiles
                if neighbor in searched_list:
                    continue

                # Exit condition --- ground open tile
                if not self.is_obstacle(*neighbor):
                    self.move_entity(a_entity, *neighbor)
                    return
                else:
                    # Searched position but haven't
                    searched_list.append(neighbor)
                    # searched positions next to it
                    to_search.append(neighbor)

            # Use list like queue to to bfs search
            neighbors = get_neighbors(*to_search.popleft())

    def get_tile(self, x, y):
        """Get namedtuple of tile location, even if out of bounds."""
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            tile_id = self.tiles[x][y]
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            new_x = x % Game.map_size
            new_y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
            tile_id = blk.tiles[new_x][new_y]
        #print "tile: {}".format(tile)
        #print "tile lookup: {}".format(self.tile_lookup[tile])
        return Tiles.tile_lookup[tile_id]

    def get_hidden(self, x, y):
        """Get hidden value on map safely with bounds checking"""
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
        return blk.hidden_map[x][y]

    def set_hidden(self, x, y, value):
        """Set hidden value on map safely with bounds checking"""
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        blk.hidden_map[x][y] = value

    def set_tile(self, x, y, new_tile):
        """Set new_tile at location"""
        #print("new_tile :{}".format(new_tile))
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        prev_tile_adj_hidden = Tiles.tile_lookup[blk.tiles[x][y]].adjacent_hidden
        blk.tiles[x][y] = new_tile
        tile_obj = Tiles.tile_lookup[new_tile]
        if prev_tile_adj_hidden != tile_obj.adjacent_hidden:
            # Adjacent hidden changed -> maybe there's a change in what's hidden
            hidden_map_handler.update_hidden_flood(self, x, y, tile_obj.adjacent_hidden)
        else:
            hidden_map_handler.update_hidden(self, x, y)

        if tile_obj.is_obstacle:
            blk.obstacle_map[x][y] = True
        else:
            blk.obstacle_map[x][y] = False

    def generate_tile_map(self):
        """Generate tiles from map function"""
        #return self.world.block_generator.generate_block( self.idx, self.idy, map_size=Game.map_size)
        return generate_block(self.world.seed_int,
                             self.idx, self.idy,
                             map_size=Game.map_size)
    def process(self):
        """Do block calculations. Manage block objects update"""
        turn = self.world.turn

        #log.info("Process block %dx%d", self.idx, self.idy)
        for a_entity in list(self.entity_list):
            if a_entity.last_move_turn >= turn:
                continue
            a_entity.last_move_turn = turn
            if not a_entity.is_dead:
                a_entity.process(self)
            else:
                a_entity.decompose(self)

    def draw_block(self,
            # Arguments for perforance
            map_size=Game.map_size, tile_lookup=Tiles.tile_lookup,
            put_char_ex=put_char_ex, min=min, max=max, wall_bg=wall_bg,
            Game=Game, range=range, xrange=xrange, hidden_map_handler=hidden_map_handler,
            gmap_min1=Game.map_size-1):
        """ Draw block terrain.
        Call assumption: The block needs to be in the drawable area
        """
        idx = self.idx
        idy = self.idy

        block_abs_x_min = map_size * idx
        block_abs_y_min = map_size * idy

        block_abs_x_max = map_size * idx + gmap_min1
        block_abs_y_max = map_size * idy + gmap_min1

        draw_x_min_abs = max(block_abs_x_min, Game.min_x)
        draw_y_min_abs = max(block_abs_y_min, Game.min_y)
        draw_x_max_abs = min(block_abs_x_max, Game.max_x)
        draw_y_max_abs = min(block_abs_y_max, Game.max_y)

        loc_x_min = draw_x_min_abs % map_size
        loc_y_min = draw_y_min_abs % map_size

        loc_x_max = draw_x_max_abs % map_size
        loc_y_max = draw_y_max_abs % map_size

        view_x = Game.view_x
        view_y = Game.view_y
        game_con = Game.game_con

        #get_tile = self.get_tile
        tiles = self.tiles
        entities = self.entities
        init_hidden = hidden_map_handler.init_hidden

        hidden_map = self.hidden_map

        #update_hidden_flood = hidden_map_handler.update_hidden_flood
        # Figure out start, end location of tiles which need to be drawn
        # for this block
        # +1 makes bound inclusive

        view_y_base = map_size * idy - view_y
        view_x_base = map_size * idx - view_x
        y_range = range(loc_y_min, loc_y_max+1)
        for x_row in xrange(loc_x_min, loc_x_max+1):
            # x grid location for the current draw
            x_loc = view_x_base + x_row

            # get y <var> for current x row -- moving these extra calls outside
            # of the inner loop
            x_tiles = tiles[x_row]
            hidden_slice = hidden_map[x_row]
            entity_slice = entities[x_row]

            for y_column in y_range:
                cur_tile = tile_lookup[x_tiles[y_column]]

                draw_char = cur_tile.char
                bg = cur_tile.bg
                fg = cur_tile.fg
                # TODO move in block gen
                # Update hidden map on the fly
                if hidden_slice[y_column] is None:
                    #if not self.get_tile(x_row, y_column).adjacent_hidden:
                    #    update_hidden_flood(self, x_row, y_column, cur_adj_hidden=True, timeout_radius=10)
                    #else:
                    init_hidden(self, x_row, y_column, cur_tile)

                # Draw top entity
                entity_cell = entity_slice[y_column]
                if entity_cell:
                    obj = entity_cell[-1]
                    draw_char = obj.char
                    if obj.fg:
                        fg = obj.fg
                    if obj.bg:
                        bg = obj.bg

                if hidden_slice[y_column]:
                    draw_char = 32 # SPACE char
                    bg = wall_bg

                put_char_ex(game_con, x_loc,
                        #y_loc
                        view_y_base + y_column,
                        draw_char, fg, bg)

    def locate(self, a_entity):
        for x_row in self.entities:
            for cell in x_row:
                for entity in cell:
                    if entity == a_entity:
                        return (entity.x, entity.y)
        return None

class DuplicateBlockError(Exception):
    def __init__(self, message, idx, idy):
        super(DuplicateBlockError, self).__init__(message)
        self.idx = idx
        self.idy = idy
