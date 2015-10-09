from game import Game 

def get_neighbors(x, y):
    """Get taxicab neighbors(4-way) from coordinates"""
    return [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]

def within_bounds(x, y):
    """Check whether local coordinates are inside its local block bounds"""
    return (0 <= x < Game.map_size and 0 <= y < Game.map_size)
