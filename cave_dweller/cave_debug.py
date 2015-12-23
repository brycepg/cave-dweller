import collections
import operator

# Check object types
def display_cur_objects(world):
    count = collections.Counter([type(obj).__name__ for aos in world.blocks.values() for obj in aos.objects])
    return count

def obj_type_per_block(world):
    count = {}
    for key in world.blocks:
        count[key] = collections.Counter([type(obj).__name__ for obj in world.blocks[key].objects])

    return count

# Num objects per block
def num_obj_per_block(world):
    return {key: len(value.objects) for key, value in world.blocks.items()}

def get_locs(block, class_type=None):
    objects = block.objects
    coords = {}
    for a_object in objects:
        if class_type:
            if not isinstance(a_object, class_type):
                continue
        coords[(a_object.x, a_object.y)] = type(a_object).__name__

    return coords
    #key_sort = sorted(coords.keys(), key=operator.itemgetter(1,2))
    #for key in key_sort:
    #    print("{}: {}".format(key, coords[key]))
