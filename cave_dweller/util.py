"""Utility functions"""
import os
import collections

def get_neighbors(x, y):
    """Get taxicab neighbors(4-way) from coordinates"""
    return [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]

def within_bounds(x, y, map_size=96):
    """Check whether local coordinates are inside its local block bounds"""
    # Not very much due to overhead of function call
    return (0 <= x < map_size and 0 <= y < map_size)

def game_path(rel_path):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    final_path = os.path.join(base_path, rel_path)
    return final_path

def equal_dicts(d1, d2, ignore_keys):
    """
    Compare dicts ignoring ignore_keys list

    returns a bool
    """

    d1_filtered = dict((k, v) for k, v in d1.iteritems() if k not in ignore_keys)
    d2_filtered = dict((k, v) for k, v in d2.iteritems() if k not in ignore_keys)
    return d1_filtered == d2_filtered

def count_entities(blk):
    """
    Utility function generate a dict counting the class of entities in a block
    arguments:
        blk - the block in question
    returns:
        a dict indexed by the class itself giving the number of that class
    """
    return collections.Counter([type(entity) for entity in blk.entity_list])
