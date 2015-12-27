import os

def get_neighbors(x, y):
    from game import Game 
    """Get taxicab neighbors(4-way) from coordinates"""
    return [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]

def within_bounds(x, y):
    from game import Game 
    """Check whether local coordinates are inside its local block bounds"""
    return (0 <= x < Game.map_size and 0 <= y < Game.map_size)

def game_path(rel_path):
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    final_path = os.path.join(base_path, rel_path)
    return final_path
