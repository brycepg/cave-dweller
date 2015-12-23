"""Container for Object and it's special subclass Player"""

import random 
import time

import libtcodpy as libtcod

from game import Game
from tiles import Id
import actions
import util

class Object(object):
    """ Non-terrain entities
        TODO: - rename to entity
              - introduce component system to make object class smaller"""
    def __init__(self, x=None, y=None, char=None):
        self.x = x
        self.y = y
        self.char = char
        self.is_dead = False
        self.is_obstacle = True
        self.edible = False
        self.initial = False

        self.bg = None
        self.fg = None

        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

        self.new_block_turn = None
        self.death_count = 0
        self.food = 1000


    def decompose(self, cur_block):
        """After death(called in world) if a body isn't consumed
           An entity will decompose and 
           be replaced with fungus after a set time"""
        self.death_count += 1
        if self.death_count > 1000:
            # Spawn decomposer in place of body
            cur_block.objects.remove(self)
            cur_block.set_object(Fungus, self.x, self.y)

    def process(self, cur_block):
        """Configuration that changes object state"""
        raise NotImplementedError

    def out_of_bounds(self):
        """Check if object is out of bounds of local
        block-coordinate system"""
        if (self.x < 0 or
                self.x >= Game.map_size or
                self.y < 0 or
                self.y >= Game.map_size):
            return True
        else:
            return False

    def move(self, coordinates, cur_block):
        """Move entity if location doesn't have an obstacle tile/entity"""
        tile = cur_block.get_tile(*coordinates)
        obj = cur_block.get_object(*coordinates)
        # Tricky if statement
        #   check if object exists before checking if it's an obstacle
        if not (obj and obj.is_obstacle) and not tile.is_obstacle:
            self.x, self.y = coordinates
            return True
        else:
            return False

    def kill(self):
        """Placeholder for death. is_dead is important for decomposing in world/block"""
        self.fg = libtcod.red
        self.bg = libtcod.darkest_red
        self.is_dead = True

class Cat(Object):
    """First dummy non-player entity. Just moves around
       TODO: eats CaveGrass/Rats
             breeding"""
    def __init__(self, x, y):
        super(Cat, self).__init__(x, y, 'c')
        self.fg = libtcod.grey

    def process(self, cur_block):
        x_new = self.x + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        y_new = self.y + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.move((x_new, y_new), cur_block)

class Spider(Object):
    """agressive entity. Kills and eats animals to survive"""
    def __init__(self, x, y):
        super(Spider, self).__init__(x, y, 'S')
        self.fg = libtcod.black
        self.MAX_HUNGER = 10000
        self.hunger = 1000 + random.randint(0, 5000)

    def process(self, cur_block):
        possible_locations = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        random.shuffle(possible_locations)
        for offset in possible_locations:
            new_loc = [self.x + offset[0], self.y + offset[1]]
            adj_object = cur_block.get_object(*new_loc)
            if adj_object and isin(ANIMALS, adj_object):
                adj_object.kill()
                adj_object.food -= 100
                self.hunger += 100
                if adj_object.food <= 0:
                    cur_block.remove_object(adj_object, *new_loc)
                    if self.hunger >= self.MAX_HUNGER:
                        cur_block.set_object(type(self), *new_loc)
                break
        else:
            self.hunger -= 1
            x_new = self.x + random.choice([-1, 0, 0, 0, 1])
            y_new = self.y + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
            self.move((x_new, y_new), cur_block)

        if self.hunger <= 0:
            self.kill()


class Mole(Object):
    """Eats fungus to survive and reproduce"""
    def __init__(self, x, y):
        super(Mole, self).__init__(x, y, 'm')
        self.fg = libtcod.sepia
        self.cur_direction = None
        self.MAX_HUNGER = 10000
        self.hunger = 1000 + random.randint(0, 1000)

    def process(self, cur_block):
        if self.initial:
            self.hunger = self.MAX_HUNGER - 1000 - random.randint(0, 5000)
            self.initial = False
        possible_locations = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        random.shuffle(possible_locations)
        for offset in possible_locations:
            new_loc = [self.x + offset[0], self.y + offset[1]]
            #if not util.within_bounds(new_loc[0], new_loc[1]) and cur_block.idx == -1 and cur_block.idy == 3:
            #    import pdb; pdb.set_trace()
            adj_object = cur_block.get_object(*new_loc)
            if adj_object and isinstance(adj_object, Fungus):
                #cur_block.objects.remove(adj_object)
                cur_block.remove_object(adj_object, *new_loc)
                if self.hunger > self.MAX_HUNGER:
                    # Spawn new mole
                    cur_block.set_object(type(self), *new_loc)
                    self.hunger -= 1000
                    break
                else:
                    # move to fungus and remove
                    self.move(new_loc, cur_block)
                    self.hunger += 100
                    break
        else:
            # No fungus
            self.hunger -= 1
            if not self.cur_direction:
                self.cur_direction = possible_locations[0]
            new_loc = [self.cur_direction[0] + self.x, self.cur_direction[1] + self.y]
            if not self.move(new_loc, cur_block):
                self.cur_direction = possible_locations[1]
            #new_loc = possible_locations[0]
            #new_loc[0] += self.x
            #new_loc[1] += self.y
            #self.move(new_loc, cur_block)
        if self.hunger == 0:
            self.kill()


class Fungus(Object):
    """Spreads from decomposed bodies and is impossible to move across"""
    def __init__(self, x, y, growth=0):
        SPONGE_BLOCK = 176
        super(Fungus, self).__init__(x, y, SPONGE_BLOCK)
        self.fg = libtcod.purple
        self.is_edible = False
        self.turns_per_growth = random.randint(90, 110)
        self.growth_turn = 0

    def process(self, cur_block):
        self.growth_turn += 1
        if self.growth_turn != 0 and self.growth_turn % self.turns_per_growth == 0:
            growth_loc = random.choice([[1, 0], [-1, 0], [0, 1], [0, -1]])
            growth_loc[0] += self.x
            growth_loc[1] += self.y
            cur_block.set_object(Fungus, growth_loc[0], growth_loc[1])

class Player(Object):
    """Player-object
       Acts as an object but also manages the viewable center"""
    def __init__(self):
        super(Player, self).__init__(Game.center_x % Game.map_size,
                                     Game.center_y % Game.map_size,
                                     '@')
        self.fg = libtcod.lightest_gray
        self.bg = None

        self.moved = False

        self.last_move_time = 0
        self.last_action_time = 0

        self.new_turn = False
        
        self.kills = 0

        # Count frames
        self.last_turn = 0
        self.register_actions()


    def register_actions(self):
        actions.Build()
        actions.Dig()
        actions.Attack()
        # Order is imporant -- move last since it doesn't require a state key
        actions.Move()
        actions.Wait()

    def process_input(self, key):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        for action in actions.PlayerAction.current_actions:
            action.get_input(key)

    def move(self, world):
        block = world.get_block(Game.center_x, Game.center_y)
        self.moved = False

        #if self.last_turn == self.world.turn:
        #    return
        #self.last_turn = self.world.turn

        if (time.time() - self.last_action_time) < Game.action_interval:
            return

        for action in actions.PlayerAction.current_actions:
            action.process(self, block)
            if self.moved:
                break

        self.last_action_time = time.time()

    def process(self, cur_block):
        self.update_draw_location(cur_block)

    def update_draw_location(self, cur_block):
        """NOTE: modifies view of game """
        Game.center_x = int(self.x + Game.map_size * cur_block.idx)
        Game.center_y = int(self.y + Game.map_size * cur_block.idy)

class CaveGrass(Object):
    """Non-movement entity. Generates cluster of grass initially"""
    def __init__(self, x, y, growth_count=0):
        UP_ARROW_CHAR = 24
        super(type(self), self).__init__(x, y, UP_ARROW_CHAR)
        self.is_obstacle = False
        self.fg = libtcod.white
        self.init_check = False
        self.growth_count = growth_count

    def process(self, cur_block):
        if not self.init_check:
            self.do_init(cur_block)
            self.init_check = True


    def do_init(self, cur_block):
        """Needs cur_block to work"""
        if self.initial:
            #print("start")
            self.growth_count = random.randint(0, 10)
        else:
            self.growth_count -= 1
        #print("count {}".format(self.growth_count))

        if self.growth_count > 0:
            possible_locations = [[1, 0], [-1, 0], [0, 1], [0, -1]]
            random.shuffle(possible_locations)
            for coordinates in possible_locations:
                new_loc = [coordinates[0] + self.x, coordinates[1] + self.y]
                tile = cur_block.get_tile(*new_loc)
                if not tile.is_obstacle and not cur_block.get_object(*new_loc):
                    cur_block.set_object(type(self), *new_loc, kw_dict={'growth_count':self.growth_count})
                    break
            else:
                pass
                #print("End of line")



class Empty(Object):
    def process(self, cur_block):
        pass

# Quick monster generation. Used in block
# Class | chance of generation for each entity | max number of entitites
generation_table = [
    [Cat, 100, 20],
    [Spider, 50, 5],
    [Fungus, 20, 20],
    [Mole, 80, 5],
    [CaveGrass, 80, 3]
]

# Utitlity function for categorizing entities
ANIMALS = [Player, Cat, Mole]
def isin(class_list, a_object):
    for a_class in class_list:
        if isinstance(a_object, a_class):
            return True
    return False
