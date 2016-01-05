"""Offload some of block hidden map functionality due to function size
get/set functions are still in block
"""

import logging
import operator
import itertools
from collections import deque

from game import Game
from util import get_neighbors

log = logging.getLogger(__name__)

def generate_map(map_size):
    """Have to generate most of the map at draw runtime due to boundry issues"""
    # TODO generate, ignore boundry tiles. Update boundry tiles when block available
    return [[None for _ in range(map_size)] for _ in range(map_size)]

def init_hidden(calling_block, x, y):
    """For drawing. Just determines if the local tile needs to be hidden if it's adjacent to all adjacent hidden blocks"""
    neighbor_tiles = [calling_block.get_tile(*coord) for coord in [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]]
    adjacent_hidden_result = [neighbor_tile.adjacent_hidden for neighbor_tile in neighbor_tiles]
    if all(adjacent_hidden_result):
        calling_block.hidden_map[x][y] = True
    else:
        calling_block.hidden_map[x][y] = False

def update_hidden(calling_block, x, y, iteration=3):
    """Updates the hidden status of a tile at x y relative to calling_block
    Used when surrounding tile state is changed

    iteration is for how many blocks to update surrounding it.
    """

    # Assumes called from coorect view?
    # TODO flood fill to determine hidden areas?
    # TODO player detection(do not make hidden if player is in them)

    # Inside map bounds
    if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
        blk = calling_block 
    else:
        # Outside map bounds - get new block
        idx_mod = x // Game.map_size
        idy_mod = y // Game.map_size
        x = x % Game.map_size
        y = y % Game.map_size
        blk = calling_block.world.get(calling_block.idx + idx_mod,
                                      calling_block.idy + idy_mod)
    # Get surrounding tiles
    neighbor_coords = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
    neighbor_tiles = [calling_block.get_tile(*coord) for coord in neighbor_coords]

    # Get surrounding tiles adjacent hidden attribute and map hidden
    adjacent_hidden_result = [neighbor_tile.adjacent_hidden for neighbor_tile in neighbor_tiles]
    hidden_map_result = [blk.get_hidden(*coord) for coord in neighbor_coords]

    # Group them together
    # If all of the surrounding tiles have either of these attributes,
    # then make the current tile hidden
    should_be_hidden = all(map(any, zip(adjacent_hidden_result, hidden_map_result)))

    if should_be_hidden:
        blk.hidden_map[x][y] = True
    else:
        blk.hidden_map[x][y] = False

    iteration -= 1
    # Now do this for the surrounding tiles too
    if not iteration < 0:
        for neighbor_coord in neighbor_coords:
            update_hidden(blk, *neighbor_coord, iteration=iteration)


def update_hidden_flood(calling_block, x, y, cur_adj_hidden, timeout_radius=Game.map_size):
    """ Detects hidden are or the destruction of a hidden area due to change of 
    tile state from calling_block at x, y

    If the cur_adj_hidden at x,y changed is False, then check for destruction
    (that is cur_adj_hidden is False)
    If cur_adj_hidden at x,y is True, then check for creation of hidden area
    (that is cur_adj_hidden is True)

    timeout_radius
        largest possile hidden area to check for before timing out
    """
    # Assumes called from coorect view?
    # TODO player detection(do not make hidden if player is in them)
    log.info("flood hidden call as %dx%d", x, y)
    if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
        blk = calling_block
    else:
        idx_mod = x // Game.map_size
        idy_mod = y // Game.map_size
        x = x % Game.map_size
        y = y % Game.map_size
        blk = calling_block.world.get(calling_block.idx + idx_mod,
                                      calling_block.idy + idy_mod)

    if cur_adj_hidden:
        log.info("New adj hidden")
        # Potentially create hidden tiles
        neighbor_coords = get_neighbors(x,y)
        valid_coords = []
        for coord in neighbor_coords:
            tile_obj = blk.get_tile(*coord)
            if not tile_obj.adjacent_hidden and not blk.get_hidden(*coord):
                valid_coords.append(coord)
        log.info("valid coords: %d", len(valid_coords))
        if len(valid_coords) > 3:
            valid_coords = []
        for coord in valid_coords:
            unhidden_list = flood_find_unhidden(blk, *coord, timeout_radius=timeout_radius)
            log.info("unHidden list: %r", unhidden_list)
            if unhidden_list:
                for loc in unhidden_list:
                    blk.set_hidden(*loc, value=True)
                for loc in unhidden_list:
                    update_hidden(blk, *loc, iteration=2)

        update_hidden(blk, x,y)
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
        if len(valid_coords) > 3:
            valid_coords = []
        for coord in valid_coords:
            log.info("flood find hidden at %dx%d", coord[0], coord[1])
            hidden_list = flood_find_hidden(blk, *coord, ign_x=x, ign_y=y, timeout_radius=timeout_radius)
            log.info("hidden list: %r", hidden_list)
            if hidden_list:
                for loc in hidden_list:
                    blk.set_hidden(*loc, value=False)
                for loc in hidden_list:
                    update_hidden(blk, *loc, iteration=1)
        update_hidden(blk, x,y)

def flood_find_hidden(calling_block, x, y, ign_x, ign_y, timeout_radius=Game.map_size):
    """Try to find hidden adjacent hidden tiles surrounding location"""
    to_search = deque()
    found_list = set([(x, y)])
    searched_list = set([(x, y), (ign_x, ign_y)])

    neighbors = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
    while True:
        for neighbor in neighbors:
            # Do not search previously searched tiles
            if neighbor in searched_list or neighbor in to_search:
                continue

            # Exit condition --- ground open tile
            if (not calling_block.get_tile(*neighbor).adjacent_hidden
                    and calling_block.get_hidden(*neighbor)):
                if max(abs(neighbor[0] - x), abs(neighbor[1] - y)) > timeout_radius:
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
            neighbors = [(search_coord[0]+1, search_coord[1]  ),
                         (search_coord[0],   search_coord[1]-1),
                         (search_coord[0]-1, search_coord[1]  ),
                         (search_coord[0],   search_coord[1]+1)]
            searched_list.add(search_coord)
        except IndexError:
            return found_list

def flood_find_unhidden(calling_block, x, y, timeout_radius=Game.map_size):
    """Try to find unhidden non-adjacent hidden tiles surrounding location"""
    log.info("flood find UNhidden at %dx%d", x, y)
    to_search = deque()
    found_list = set([(x, y)])
    searched_list = set((x, y))

    neighbors = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
    while True:
        for neighbor in neighbors:
            # Do not search previously searched tiles
            if neighbor in searched_list or neighbor in to_search:
                continue

            # Exit condition --- ground open tile
            if (not calling_block.get_tile(*neighbor).adjacent_hidden
                    and not calling_block.get_hidden(*neighbor)):
                if max(abs(neighbor[0] - x), abs(neighbor[1] - y)) > timeout_radius:
                    log.info("neighbor %r too far away", neighbor)
                    return None
                found_list.add(neighbor)
                to_search.append(neighbor)
            else:
                searched_list.add(neighbor)

        # Use list like queue to to bfs search
        try:
            search_coord = to_search.popleft()
            neighbors = [(search_coord[0]+1, search_coord[1]  ),
                         (search_coord[0],   search_coord[1]-1),
                         (search_coord[0]-1, search_coord[1]  ),
                         (search_coord[0],   search_coord[1]+1)]
            searched_list.add(search_coord)
        except IndexError:
            return found_list
