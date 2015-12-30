"""container for Block"""

import random
import logging
import operator
import itertools

import libtcodpy as libtcod

from gen_map import generate_block
from gen_map import generate_obstacle_map
from gen_map import generate_hidden_map
from game import Game
from tiles import Tiles
import entities
from util import get_neighbors

log = logging.getLogger(__name__)

class Block:
    """Segment of world populated by object and terrain"""
    def __init__(self, idx, idy, world, tiles=None, entities=None,
                 obstacle_map=None, hidden_map=None, load_turn=0):
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

        if not obstacle_map:
            self.obstacle_map = generate_obstacle_map(self.tiles,
                                                      Game.map_size)
        else:
            self.obstacle_map = obstacle_map

        if not entities:
            self.entities = [[[] for _ in range(Game.map_size)] for _ in range(Game.map_size)]
            self.generate_entities(self.entities)
        else:
            self.entities = entities

        if not hidden_map:
            self.hidden_map = generate_hidden_map(Game.map_size)
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

    def generate_entities(self, entity_array):
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
        """Remove object at location relative to block coordinates"""
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
        return a_entity

    def get_entity(self, x, y):
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

    def reposition_entity(self, a_entity):
        """Breadth first search for nearest non-obstacle to reposition object
        if's its stuck in an obstacle during generation"""

        if not self.get_tile(a_entity.x, a_entity.y).is_obstacle:
            return
        searched_list = [(a_entity.x, a_entity.y)]
        to_search = []
        neighbors = get_neighbors(a_entity.x, a_entity.y)

        while True:
            for neighbor in neighbors:
                # Do not search previously searched tiles
                if neighbor in searched_list:
                    continue

                # Exit condition --- ground open tile
                if not self.is_obstacle(*neighbor):
                    self.move_entity(a_entity, *neighbor)
                    #a_entity.x, a_entity.y = neighbor
                    return
                else:
                    # Searched position but haven't
                    searched_list.append(neighbor)
                    # searched positions next to it
                    to_search.append(neighbor)

            # Use list like queue to to bfs search
            neighbors = get_neighbors(*to_search.pop(0))

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
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
        return blk.hidden_map[x][y]

    def update_hidden(self, x, y, iteration=2):
        # Assumes called from coorect view?
        # TODO flood fill to determine hidden areas?
        # TODO player detection(do not make hidden if player is in them)
        # TODO make work for init draw
        if iteration < 0:
            return
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
        iteration -= 1
        cur_tile = blk.get_tile(x,y)
        neighbor_coords = get_neighbors(x,y)
        neighbor_tiles = itertools.starmap(blk.get_tile, neighbor_coords)
        adjacent_hidden = operator.attrgetter('adjacent_hidden')
        obstacle_result = map(adjacent_hidden, neighbor_tiles)
        hidden_map_result = list(itertools.starmap(blk.get_hidden, neighbor_coords))
        should_be_hidden = all(map(any, zip(obstacle_result, hidden_map_result)))
        if should_be_hidden:
            blk.hidden_map[x][y] = True
        else:
            blk.hidden_map[x][y] = False
        for neighbor_coord in neighbor_coords:
            blk.update_hidden(*neighbor_coord, iteration=iteration)




    def set_tile(self, x, y, tile):
        """Set tile at location"""
        #print("tile :{}".format(tile))
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        blk.tiles[x][y] = tile
        blk.update_hidden(x, y)
        if Tiles.tile_lookup[tile].is_obstacle:
            blk.obstacle_map[x][y] = True
        else:
            blk.obstacle_map[x][y] = False

    def generate_tile_map(self):
        """Generate tiles from map function"""
        return generate_block(self.world.perlin_seed,
                              self.idx, self.idy,
                              map_size=Game.map_size)
    def process(self):
        """Do block calculations. Manage block objects update"""
        turn = self.world.turn

        #log.info("Process block %dx%d", self.idx, self.idy)
        for line in self.entities:
            for cell in line:
                for a_entity in cell:
                    if a_entity.last_move_turn >= turn:
                        continue
                    a_entity.last_move_turn = turn
                    if not a_entity.is_dead:
                        a_entity.process(self)
                    else:
                        a_entity.decompose(self)

        ## Reverse enumerate to allow removal of object
        #for i, a_object in reversed(list(enumerate(objects))):
        #    if a_object.out_of_bounds():
        #        # Transfer object to new block-coordinate system
        #        free_agent = objects[a_object.x][a_object.y].remove(a_object)
        #        idx_mod = a_object.x // map_size
        #        idy_mod = a_object.y // map_size
        #        a_object.x = a_object.x % map_size
        #        a_object.y = a_object.y % map_size
        #        new_block = self.world.get(idx + idx_mod,
        #                                   idy + idy_mod)
        #        #log.debug("object crossed border at {} {}x{}".format(a_object,
        #        #                                        a_object.x,
        #        #                                        a_object.y))
        #        new_block.objects.append(free_agent)

    def draw_block(self):
        """ Draw block terrain.
        Call assumption: The block needs to be in the drawable area
        """
        #self.block_generator = libtcod.random_new_from_seed(self.block_seed)
        #block_generator = self.block_generator
        #random_get_int = libtcod.random_get_int
        map_size = Game.map_size

        block_abs_x_min = map_size * self.idx
        block_abs_y_min = map_size * self.idy

        block_abs_x_max = map_size * (self.idx+1) - 1
        block_abs_y_max = map_size * (self.idy+1) - 1

        draw_x_min_abs = max(block_abs_x_min, Game.min_x)
        draw_y_min_abs = max(block_abs_y_min, Game.min_y)
        draw_x_max_abs = min(block_abs_x_max, Game.max_x)
        draw_y_max_abs = min(block_abs_y_max, Game.max_y)

        loc_x_min = draw_x_min_abs % map_size
        loc_y_min = draw_y_min_abs % map_size

        loc_x_max = draw_x_max_abs % map_size
        loc_y_max = draw_y_max_abs % map_size

        idx = self.idx
        idy = self.idy

        view_x = Game.view_x
        view_y = Game.view_y
        game_con = Game.game_con

        get_tile = self.get_tile
        tile_lookup = Tiles.tile_lookup
        tiles = self.tiles
        entities = self.entities

        hidden_map = self.hidden_map
        # Figure out start, end location of tiles which need to be drawn
        # for this block
        # +1 makes bound inclusive
        for x_row in range(loc_x_min, loc_x_max+1):
            abs_x = map_size * idx + x_row
            x_tiles = tiles[x_row]
            hidden_slice = hidden_map[x_row]
            for y_column in range(loc_y_min, loc_y_max+1):
                abs_y = map_size * idy + y_column
                cur_tile = tile_lookup[x_tiles[y_column]]

                draw_char = cur_tile.char
                bg = cur_tile.bg
                fg = cur_tile.fg
                if hidden_slice[y_column] is None:
                    self.update_hidden(x_row, y_column)
                    #if(get_tile(x_row+1, y_column).adjacent_hidden and
                    #   get_tile(x_row-1, y_column).adjacent_hidden and
                    #   get_tile(x_row, y_column+1).adjacent_hidden and
                    #   get_tile(x_row, y_column-1).adjacent_hidden):
                    #    hidden_slice[y_column] = True
                    #else:
                    #    hidden_slice[y_column] = False

                if cur_tile.attributes:
                    chars = cur_tile.attributes.get('alternative_characters')
                    if chars:
                        char_choice = 2
                        if char_choice != len(chars):
                            draw_char = chars[char_choice]
                        else:
                            draw_char = cur_tile.char
                entity_cell = self.entities[x_row][y_column]
                if entity_cell:
                    obj = entity_cell[-1]
                    draw_char = obj.char
                    if obj.fg:
                        fg = obj.fg
                    if obj.bg:
                        bg = obj.bg

                if hidden_slice[y_column]:
                    draw_char = ' '
                    bg = Tiles.wall.bg

                libtcod.console_put_char_ex(game_con,
                        abs_x - view_x,
                        abs_y - view_y,
                        draw_char, fg, bg)

    def locate(self, a_entity):
        for x_row in self.entities:
            for cell in x_row:
                for entity in cell:
                    if entity == a_entity:
                        return (entity.x, entity.y)
        return None
