"""Container for Entity and it's special subclass Player"""

import random
import time
import logging
import colors

from game import Game
import actions

log = logging.getLogger(__name__)

class Entity(object):
    """ Non-terrain entities
        TODO: - rename to entity
              - introduce component system to make object class smaller"""
    def __init__(self, x=None, y=None, char=None):
        self.x = x
        self.y = y
        if type(char) == str or type(char) == bytes:
            self.char = ord(char)
        else:
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

        self.last_move_turn = None
        self.death_count = 0
        self.food = 1000
        self.cur_block = None

    def __eq__(self, entity):
        return (isinstance(entity, type(self)) and
                util.equal_dicts(self.__dict__, entity.__dict__, ['cur_block']))

    def decompose(self, cur_block):
        """After death(called in world) if a body isn't consumed
           An entity will decompose and
           be replaced with fungus after a set time"""
        self.death_count += 1
        if self.death_count > 1000:
            # Spawn decomposer in place of body
            cur_block.remove_entity(self, self.x, self.y)
            cur_block.set_entity(Fungus, self.x, self.y)

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
        if not cur_block.is_obstacle(*coordinates):
            cur_block.move_entity(self, *coordinates)
            return True
        else:
            return False

    def kill(self):
        """Placeholder for death. is_dead is important for decomposing in world/block"""
        self.fg = colors.red
        self.bg = colors.darkest_red
        self.is_dead = True

class Cat(Entity):
    """First dummy non-player entity. Just moves around
       TODO: eats CaveGrass/Rats
             breeding"""
    def __init__(self, x, y):
        super(Cat, self).__init__(x, y, 'c')
        self.fg = colors.gray

    def process(self, cur_block):
        x_new = self.x + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        y_new = self.y + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
        self.move((x_new, y_new), cur_block)

class Spider(Entity):
    """agressive entity. Kills and eats animals to survive"""
    def __init__(self, x, y):
        super(Spider, self).__init__(x, y, 'S')
        self.fg = colors.black
        self.MAX_HUNGER = 10000
        self.hunger = 1000 + random.randint(0, 5000)

    def process(self, cur_block):
        possible_locations = [[1, 0], [-1, 0], [0, 1], [0, -1]]
        random.shuffle(possible_locations)
        for offset in possible_locations:
            new_loc = [self.x + offset[0], self.y + offset[1]]
            adj_entity = cur_block.get_entity(*new_loc)
            if adj_entity and isin(ANIMALS, adj_entity):
                adj_entity.kill()
                adj_entity.food -= 100
                self.hunger += 100
                if adj_entity.food <= 0:
                    cur_block.remove_entity(adj_entity, *new_loc)
                    if self.hunger >= self.MAX_HUNGER:
                        if not cur_block.is_obstacle(*new_loc):
                            cur_block.set_entity(type(self), *new_loc)
                break
        else:
            self.hunger -= 1
            x_new = self.x + random.choice([-1, 0, 0, 0, 1])
            y_new = self.y + random.choice([-1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1])
            self.move((x_new, y_new), cur_block)

        if self.hunger <= 0:
            self.kill()


class Mole(Entity):
    """Eats fungus to survive and reproduce"""
    def __init__(self, x, y):
        super(Mole, self).__init__(x, y, 'm')
        self.fg = colors.sepia
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
            adj_entity = cur_block.get_entity(*new_loc)
            if adj_entity and isinstance(adj_entity, Fungus):
                cur_block.remove_entity(adj_entity, *new_loc)
                if self.hunger > self.MAX_HUNGER:
                    # Spawn new mole
                    if not cur_block.is_obstacle(*new_loc):
                        cur_block.set_entity(type(self), *new_loc)
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


class Fungus(Entity):
    """Spreads from decomposed bodies and is impossible to move across"""
    def __init__(self, x, y, growth=0):
        SPONGE_BLOCK = 176
        super(Fungus, self).__init__(x, y, SPONGE_BLOCK)
        self.fg = colors.purple
        self.is_edible = False
        self.turns_per_growth = random.randint(90, 110)
        self.growth_turn = 0

    def process(self, cur_block):
        """Randomly spread every turns_per_growth"""
        self.growth_turn += 1
        if self.growth_turn != 0 and self.growth_turn % self.turns_per_growth == 0:
            growth_loc = random.choice([[1, 0], [-1, 0], [0, 1], [0, -1]])
            growth_loc[0] += self.x
            growth_loc[1] += self.y
            if not cur_block.is_obstacle(*growth_loc):
                cur_block.set_entity(Fungus, *growth_loc)

class Player(Entity):
    """Player-object
       Acts as an object but also manages the viewable center"""
    def __init__(self):
        super(Player, self).__init__(Game.map_size//2,
                                     Game.map_size//2,
                                     '@')
        self.fg = colors.lightest_gray
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
        """Register action subclasses into internal list"""
        actions.PlayerAction.register(actions.Build)
        actions.PlayerAction.register(actions.Dig)
        actions.PlayerAction.register(actions.Attack)
        # Order is imporant -- move last since it doesn't require a state key
        actions.PlayerAction.register(actions.Move)
        # Register wait after move to allow movement while in fast mode
        actions.PlayerAction.register(actions.Wait)

    def process_input(self, key):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        for action in actions.PlayerAction.current_actions:
            action.get_input(key)

    def move(self, world):
        """Run player actions if within ime interval"""
        block = world.get_block(Game.view_x + Game.game_width//2, Game.view_y + Game.game_height//2)
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
        return

    def update_view_location(self):
        """NOTE: modifies view of game """
        cur_block = self.cur_block
        Game.view_x = int(self.x + Game.map_size * cur_block.idx - Game.game_width//2)
        Game.view_y = int(self.y + Game.map_size * cur_block.idy - Game.game_height//2)
        Game.update_view()

class CaveGrass(Entity):
    """Non-movement entity. Generates cluster of grass initially"""
    def __init__(self, x, y, growth_count=0, cur_block=None):
        UP_ARROW_CHAR = 24
        super(type(self), self).__init__(x, y, UP_ARROW_CHAR)
        self.is_obstacle = False
        self.fg = colors.white
        self.init_check = False
        self.growth_count = growth_count
        if cur_block:
            self.process(cur_block)

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
                if not tile.is_obstacle and not cur_block.get_entity(*new_loc):
                    cur_block.set_entity(type(self), *new_loc, kw_dict={'growth_count':self.growth_count, 'cur_block': cur_block})
                    break
            else:
                pass
                #print("End of line")



class Empty(Entity):
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

def isin(class_list, a_entity):
    """Check if a class is in a list of classes"""
    for a_class in class_list:
        if isinstance(a_entity, a_class):
            return True
    return False
