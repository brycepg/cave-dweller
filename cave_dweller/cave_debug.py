"""Debug info functions"""
import collections

from . import libtcodpy as libtcod

from .game import Game

# TODO fix with entities update

# Check entity types
def display_cur_entities(world):
    """
    Get count of entity classes in all active blocks

    arguments:
        world to extract blocks from

    returns a dict which contains the count of each class indexed py class name
    """
    count = collections.Counter([type(entity).__name__
                                 for block in world.blocks.values()
                                 for entity in block.entity_list])
    return count

def obj_type_per_block(world):
    """
    Get entity type counts for each block

    arguments:
        world to grab blocks from

    Returns:
        dict of entity counts for each block indexed by class name
    """
    count = {}
    for key in world.blocks:
        count[key] = collections.Counter([type(entity).__name__ for entity in world.blocks[key].entity_list])

    return count

# Num entities per block
def num_obj_per_block(world):
    """
    arguments:
        world to get blocks from
    returns:
        dict of blocks and the total entity count for each
    """
    return {key: len(value.entities) for key, value in world.blocks.items()}

def get_locs(block, class_type=None):
    """
    Get the coordinates of entities in block that match class_type

    arguments:
        block - block to get info from
        class_type - entity class
    returns:
        dict of coordinate pair - entity reference for the block
    """
    entities = block.entities
    coords = {}
    for a_entity in entities:
        if class_type:
            if not isinstance(a_entity, class_type):
                continue
        coords[(a_entity.x, a_entity.y)] = type(a_entity).__name__

    return coords

def debug_print(**kwargs):
    """Pass locals of main loop to print debug information"""
    #exec("") # Avoid locals optimization to allow locals update hack
    #locals().update(args)
    fps_base = kwargs['fps_base']
    world = kwargs['world']
    game = kwargs['game']
    player = kwargs['player']
    spent_time = kwargs['spent_time']

    libtcod.console_print(Game.debug_con, 1, 1, "FPS: %s" % (str(int(1/fps_base))))
    libtcod.console_print(Game.debug_con, 1, 2, "active blocks: %d" % len(world.blocks))
    libtcod.console_print(Game.debug_con, 1, 3, "inactive blocks: %d" % len(world.inactive_blocks))
    libtcod.console_print(Game.debug_con, 1, 4, "block: (%d,%d)" % (game.idx_cur, game.idy_cur))
    libtcod.console_print(Game.debug_con, 1, 5, "view: (%dx%d)" % (game.view_x, game.view_y))
    libtcod.console_print(Game.debug_con, 1, 6, "player: (%dx%d)" % (player.x, player.y))
    libtcod.console_print(Game.debug_con, 1, 7, "process/draw time: ({0:.4f})".format(spent_time))
    num_entities = sum([len(block.entity_list) for block in world.blocks.values()])
    libtcod.console_print(Game.debug_con, 1, 8, "entities: {}".format(num_entities))
