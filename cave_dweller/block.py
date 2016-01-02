"""container for Block"""

import random
import logging
import operator
import itertools
from collections import deque

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
            self.entities = [[[] for _ in range(Game.map_size)]
                             for _ in range(Game.map_size)]
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
                if not self.is_obstacle(*neighbor):# and not (avoid_hidden or 
                                                  #          self.get_hidden(*neighbor)):
                    self.move_entity(a_entity, *neighbor)
                    #a_entity.x, a_entity.y = neighbor
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
        if not iteration < 0:
            for neighbor_coord in neighbor_coords:
                blk.update_hidden(*neighbor_coord, iteration=iteration)

    def update_hidden_flood(self, x, y, cur_adj_hidden):
        # Assumes called from coorect view?
        # TODO flood fill to determine hidden areas?
        # TODO player detection(do not make hidden if player is in them)
        log.info("flood hidden call")
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        if cur_adj_hidden:
            log.info("New adj hidden")
            # Potentially created hidden tiles
            neighbor_coords = get_neighbors(x,y)
            valid_coords = []
            for coord in neighbor_coords:
                tile_obj = blk.get_tile(*coord)
                if not tile_obj.adjacent_hidden and blk.get_hidden(*coord):
                    valid_coords.append(coord)
            log.info("valid coords: %d", len(valid_coords))
            if len(valid_coords) > 2:
                valid_coords = []
            for coord in valid_coords:
                unhidden_list = self.flood_find_unhidden(*coord)
                log.info("unHidden list: %r", unhidden_list)
                if unhidden_list:
                    for loc in unhidden_list:
                        self.set_hidden(*loc, value = True)
                    for loc in unhidden_list:
                        self.update_hidden(*loc, iteration=2)
            else:
                self.update_hidden(x,y)
            if not valid_coords:
                self.update_hidden(x,y)


        else:
            # Unmasking hidden tiles
            log.info("try unhidden")
            neighbor_coords = get_neighbors(x,y)
            log.info("-neighbors %r", neighbor_coords)
            valid_coords = []
            for coord in neighbor_coords:
                tile_obj = blk.get_tile(*coord)
                if not tile_obj.adjacent_hidden and blk.get_hidden(*coord):
                    valid_coords.append(coord)

            # No need to update a tile placed in an open area
            if len(valid_coords) > 2:
                valid_coords = []
            for coord in valid_coords:
                log.info("flood find hidden at %dx%d", coord[0], coord[1])
                hidden_list = self.flood_find_hidden(*coord, ign_x=x, ign_y=y)
                log.info("hidden list: %r", hidden_list)
                if hidden_list:
                    for loc in hidden_list:
                        self.set_hidden(*loc, value = False)
                    for loc in hidden_list:
                        self.update_hidden(*loc, iteration=1)
            else:
                self.update_hidden(x,y)
            if not valid_coords:
                self.update_hidden(x,y)

    def set_hidden(self, x, y, value):
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            blk = self
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            x = x % Game.map_size
            y = y % Game.map_size
            blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)

        blk.hidden_map[x][y] = value

    def flood_find_hidden(self, x, y, ign_x, ign_y):
        to_search = deque()
        found_list = set([(x, y)])
        searched_list = set([(x, y), (ign_x, ign_y)])

        neighbors = get_neighbors(x, y)
        while True:
            for neighbor in neighbors:
                # Do not search previously searched tiles
                if neighbor in searched_list:
                    continue

                # Exit condition --- ground open tile
                if not self.get_tile(*neighbor).adjacent_hidden and self.get_hidden(*neighbor):
                    if max(abs(neighbor[0] - x), abs(neighbor[1] - y)) > 10:
                        print(to_search)
                        log.info("neighbor %r too far away", neighbor)
                        return None
                    found_list.add(neighbor)
                    to_search.append(neighbor)
                else:
                    searched_list.add(neighbor)

            # Use list like queue to to bfs search
            try:
                log.info("len %d", len(to_search))
                search_coord = to_search.popleft()
                neighbors = get_neighbors(*search_coord)
                searched_list.add(search_coord)
            except IndexError:
                return found_list

    def flood_find_unhidden(self, x, y):
        log.info("flood find at %dx%d", x, y)
        to_search = deque()
        found_list = [(x, y)]
        searched_list = [(x, y)]

        neighbors = get_neighbors(x, y)
        while True:
            for neighbor in neighbors:
                # Do not search previously searched tiles
                if neighbor in searched_list:
                    continue

                # Exit condition --- ground open tile
                if (not self.get_tile(*neighbor).adjacent_hidden
                        and not self.get_hidden(*neighbor)):
                    if max(abs(neighbor[0] - x), abs(neighbor[1] - y)) > 10:
                        log.info("neighbor %r too far away", neighbor)
                        return None
                    found_list.append(neighbor)
                    to_search.append(neighbor)
                else:
                    searched_list.append(neighbor)

            # Use list like queue to to bfs search
            try:
                search_coord = to_search.popleft()
                neighbors = get_neighbors(*search_coord)
                searched_list.append(search_coord)
            except IndexError:
                return found_list

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
            blk.update_hidden_flood(x, y, tile_obj.adjacent_hidden)
        else:
            blk.update_hidden(x, y)
        #blk.update_hidden(x, y)

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

    def draw_block(self):
        """ Draw block terrain.
        Call assumption: The block needs to be in the drawable area
        """
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
                # TODO move in block gen
                if hidden_slice[y_column] is None:
                    self.update_hidden(x_row, y_column)

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
