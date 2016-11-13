import logging

from game import Game

import libtcodpy as libtcod

log = logging.getLogger(__name__)

def is_obstacle_abs(world, abs_x, abs_y):
    """Return obstacle status from abs tile coordinate"""
    idx = abs_x // Game.map_size
    idy = abs_y // Game.map_size
    blk = world.get(idx, idy)
    x = abs_x % Game.map_size
    y = abs_y % Game.map_size
    return blk.obstacle_map[x][y]

def move_entity_abs(world, entity, cur_blk, new_abs_x, new_abs_y):
    dst_idx = new_abs_x // Game.map_size
    dst_idy = new_abs_y // Game.map_size
    dst_blk = world.get(dst_idx, dst_idy)

    new_dst_x = new_abs_x % Game.map_size
    new_dst_y = new_abs_y % Game.map_size
    # ASSUMES ENTITY is owned by cur_block
    if not cur_block.get_tile(entity.x,entity.y).is_obstacle:
        cur_block.obstacle_map[entity.x][entity.y] = False
    cur_block.entities[entity.x][entity.y].remove(entity)
    entity.x = new_dst_x
    entity.y = new_dst_y

    dst_blk.entities[entity.x][entity.y].append(entity)
    if entity.is_obstacle:
        dst_blk.obstacle_map[entity.x][entity.y] = True
    # Use return block to know where the object is
    return dst_blk

def move_player(player, cur_block, dst_x_abs, dst_y_abs):


class FovMap(object):
    def __init__(self):
        self.fov_map = libtcod.map_new(Game.game_width, Game.game_height)
        self.path = None
        self.x_start = None
        self.y_start = None

    def populate_map(self, world, abs_x_start, abs_y_start):
        self.x_start = abs_x_start
        self.y_start = abs_y_start
        log.info("game width %d", Game.game_width)
        log.info("game height %d", Game.game_height)
        for x in range(Game.game_width):
            for y in range(Game.game_height):
                is_walkable = not is_obstacle_abs(world, abs_x_start + x, abs_y_start + y)
                libtcod.map_set_properties(self.fov_map, x, y, True, is_walkable)

    def create_path(self):
        self.path = libtcod.path_new_using_map(self.fov_map, dcost=0.0)

    def compute_path(self, src_x, src_y, dst_x, dst_y):
        libtcod.path_compute(self.path, src_x, src_y, dst_x, dst_y)

    def compute_path_abs(self, abs_src_x, abs_src_y, abs_dst_x, abs_dst_y):
        src_x = abs_src_x - self.x_start 
        src_y = abs_src_y - self.y_start 
        dst_x = abs_dst_x - self.x_start 
        dst_y = abs_dst_y - self.y_start 
        libtcod.path_compute(self.path, src_x, src_y, dst_x, dst_y)

    def get_coord_abs(self):
        x, y = libtcod.path_walk(self.path, False)
        abs_x = x + self.x_start
        abs_y = y + self.y_start
        return abs_x, abs_y


    def test(self, abs_src_x, abs_src_y, abs_dst_x, abs_dst_y):
        self.compute_path_abs(abs_src_x, abs_src_y, abs_dst_x, abs_dst_y)
        if libtcod.path_is_empty(self.path):
            log.info("Path is empty")
        while True:
            loc = libtcod.path_walk(self.path, False)
            if loc != (None, None):
                loc_abs = (loc[0] + self.x_start, loc[1] + self.y_start)
                log.info("abs ({},{})".format(*loc_abs))
                #print("({},{})".format(*loc))
            else:
                break
