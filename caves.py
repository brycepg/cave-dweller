#!/usr/bin/env python3
""" Call this file to start the game
Stores initalization of game, main game loop
And command-line argument processing
"""

__author__ = "Bryce Guinta"
__contact__ = "azrathud@gmail.com"
__version__ = "0.0.2"

import argparse
import sys
import time
import random
import os
import logging

import pygame
from pygame.locals import *
import pygcurse

from gen_map import generate_map_slice

class GetOutOfLoop(Exception):
    pass

class Block:
    def __init__(self, idx, idy, world):
        #self.delay_generation = False if len(world.blocks) <= 1 else True
        self.delay_generation = False
        self.world = world
        self.chars = []
        self.is_obstacle = []
        self.objects = []
        self.idx = idx
        self.idy = idy

        self.completely_generated = False
        self.y_coord_gen_num = 0
        self.init_map_slices()


    def init_map_slices(self):
        """Generate block in 'slices' to allow a 
            'timeout' after a certain threshold
             To allow other parts of the game to update."""
        while not Game.past_loop_time() or not self.delay_generation:
            #print(self.world.perlin_seed)
            num_map_slice = generate_map_slice(self.world.perlin_seed,
                                               self.idx,
                                               self.idy,
                                               self.y_coord_gen_num,
                                               map_size=Game.map_size)
            char_line = []
            is_obstacle_line = []

            for val in num_map_slice:
                if val == 255:
                    char_line.append('x')
                    is_obstacle_line.append(True)
                else:
                    char_line.append('-')
                    is_obstacle_line.append(False)
            self.chars.append(char_line)
            self.is_obstacle.append(is_obstacle_line)
            self.y_coord_gen_num += 1
            if self.y_coord_gen_num >= Game.map_size:
                self.completely_generated = True
                break
        if Game.past_loop_time():
            print("past_time")
    def process(self):
        """Do block calculations. Manage block objects update"""
        if not self.completely_generated:
            self.init_map_slices()
            return
        new_blocks = []

        for a_object in self.objects:
            a_object.move(self)

        for i, a_object in reversed(list(enumerate(self.objects))):
            if a_object.out_of_bounds():
                # Transfer object to new block-coordinate system
                if a_object.x >= Game.map_size:
                    new_block = Block(self.idx+1, self.idy, self.world)
                    a_object.x = a_object.x % Game.map_size
                elif a_object.x < 0:
                    new_block = Block(self.idx-1, self.idy, self.world)
                    a_object.x = Game.map_size + a_object.x
                elif a_object.y >= Game.map_size:
                    new_block = Block(self.idx, self.idy+1, self.world)
                    a_object.y = a_object.y % Game.map_size
                elif a_object.y < 0:
                    new_block = Block(self.idx, self.idy-1, self.world)
                    a_object.y = Game.map_size + a_object.y
                print("a_object {} {}x{}".format(a_object, a_object.x, a_object.y))
                free_agent = self.objects.pop(i)
                new_block.objects.append(free_agent)
                new_blocks.append(new_block)

        return new_blocks

    def draw(self):
        """Draw block cells that are in frame"""
        if not self.completely_generated:
            return
        self.draw_block()
        self.draw_objects()

    def draw_block(self):
        """Draw block terrain"""
        for row in range(Game.map_size):
            abs_y = Game.map_size * self.idy + row
            for column in range(Game.map_size):
                abs_x = Game.map_size * self.idx + column
                if((Game.min_x <= abs_x <= Game.max_x) and
                   (Game.min_y <= abs_y <= Game.max_y)):
                    if self.is_obstacle[row][column]:
                        fg = 'white'
                    else:
                        fg = 'gray'
                    #print('{}x{}'.format(abs_x, abs_y), end=",")
                    Game.win.putchar(self.chars[row][column],
                            abs_x - Game.center_x + Game.screen_width//2,
                            abs_y - Game.center_y + Game.screen_height//2, fg)
    def draw_objects(self):
        """Put block's drawable objects on screen"""
        for a_object in self.objects:
            abs_x = Game.map_size * self.idx + a_object.x
            abs_y = Game.map_size * self.idy + a_object.y
            if Game.in_drawable_coordinates(abs_x, abs_y):
                Game.win.putchar(a_object.char,
                                 (abs_x - Game.center_x +
                                  Game.screen_width//2),
                                 (abs_y - Game.center_y +
                                  Game.screen_height//2))

class World:
    def __init__(self, rand_seed=None):
        self.loaded_block_radius = 256 // Game.map_size

        self.generate_seeds(rand_seed)
        self.blocks = {}
        #self.init_blocks()

    def generate_seeds(self, rand_seed):
        """Generate time seed if not given
           Seed rand
           Generate reduced size seed for C perlin function"""
        if rand_seed is None:
            rand_seed = time.time()
        # Do not use floating point time
        rand_seed = int(rand_seed)
        print(rand_seed)

        self.rand_seed = rand_seed

        # Seed random
        random.seed(self.rand_seed)

        # Seed for perlin noise -- doesn't work with big numbers?
        # Probably due to variable size constraints in C
        self.perlin_seed = random.randrange(-65565, 65565)

    def cull_old_block(self):
        """ Delete blocks father than loaded_block_radius blocks away from the player
            Note: Only destroys one block per call
        """
        # TODO serialize old blocks
        destroy_block = None
        for key in self.blocks:
            if (abs(Game.idx_cur - self.blocks[key].idx) > self.loaded_block_radius or
                    abs(Game.idy_cur - self.blocks[key].idy) > self.loaded_block_radius):
                destroy_block = key
                break
        if destroy_block:
            del self.blocks[key]



    def load_surrounding_blocks(self):
        """Loads blocks surrounding player specified by loaded_block_radius"""
        # Load the current block immediately
        cur_blk = self.get(Game.idx_cur, Game.idy_cur)
        try:
            for idy in range(Game.idy_cur - self.loaded_block_radius, Game.idy_cur + self.loaded_block_radius + 1):
                for idx in range(Game.idx_cur - self.loaded_block_radius, Game.idx_cur + self.loaded_block_radius + 1):
                    self.get(idx, idy)
                    if Game.past_loop_time():
                        raise GetOutOfLoop
        except GetOutOfLoop:
            print('load timeout')
            pass

    def get(self, idx, idy):
        """Generate requested block and return reference
        Python doesn't like negative indices. use idx,idy coordinates as hash table
        Required since each block is dynamically generated
        """
        try:
            block = self.blocks[(idx, idy)]
        except KeyError:
            block = Block(idx, idy, self)
            self.blocks[(idx, idy)] = block

        return block

    def process(self):
        self.cull_old_block()
        self.load_surrounding_blocks()
        new_blocks = []
        for block in self.blocks.values():
            gen_blks = block.process()
            if gen_blks:
                new_blocks += gen_blks

        if new_blocks:
            print("{} {}x{}".format(new_blocks[0], new_blocks[0].idx, new_blocks[0].idy))
        for block in new_blocks:
            self.blocks[(block.idx, block.idy)] = block

    def draw(self):
        """Call block's draw functions(as to be separate from game logic"""
        for block in self.blocks.values():
            block.draw()

class Object:
    """ Non-terrain entities"""
    def __init__(self, x=None, y=None, char=None):
        self.x = x
        self.y = y
        self.char = char

        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False

    def move(self, cur_block):
        """Configuration that changes object state"""
        pass

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

class Player(Object):
    """Player-object
       Acts as an object but also manages the viewable center"""
    def __init__(self):
        super().__init__(Game.center_x % Game.map_size, Game.center_y % Game.map_size, '@')
        self.step_modifier = 1

    def process_input(self, event):
        """ Process event keys -- set state of player
        If key held down -- keep movement going
        If key released -- stop movement
        """
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self.move_down = False
                self.move_up = True
            if event.key == K_DOWN:
                self.move_up = False
                self.move_down = True
            if event.key == K_LEFT:
                self.move_right = False
                self.move_left = True
            if event.key == K_RIGHT:
                self.move_left = False
                self.move_right = True
        elif event.type == KEYUP:
            if event.key == K_UP:
                self.move_up = False
            if event.key == K_DOWN:
                self.move_down = False
            if event.key == K_LEFT:
                self.move_left = False
            if event.key == K_RIGHT:
                self.move_right = False

    def move(self, cur_block):
        """ Player movement: 
            NOTE: modifies view of game """
        if Game.fast:
            self.step_modifier = 10

        step = 1 * self.step_modifier

        for _ in range(step):
            if self.move_up:
                self.y -= 1
                Game.center_y -= 1
            if self.move_down:
                self.y += 1
                Game.center_y += 1
            if self.move_left:
                self.x -= 1
                Game.center_x -= 1
            if self.move_right:
                self.x += 1
                Game.center_x += 1

class Game:
    map_size = 64

    screen_width = 64
    screen_height = 54

    debug = True
    fast = False
    fps = 5

    # Drawable window
    win = None

    # Center coordinates of drawable area
    center_x = 0
    center_y = 0
    center_x = screen_width // 2
    center_y = screen_height // 2

    # Bound coordinates of drawable area
    min_x = None
    min_y = None
    max_x = None
    max_y = None

    # Current view block coordinates
    idx_cur = None
    idy_cur = None

    win = None

    loop_start = None
    loop_time = 1/fps

    @classmethod
    def in_drawable_coordinates(cls, abs_x, abs_y):
        """Check if absolute coordinate is in drawable area"""
        if(cls.min_x <= abs_x <= cls.max_x
           and cls.min_y <= abs_y <= cls.max_y):
            return True
        else:
            return False

    def __init__(self):
        # TODO
        #self.text_font = pygame.font.SysFont("monospace", 15)
        Game.win = pygcurse.PygcurseWindow(self.screen_width,
                                           self.screen_height,
                                           fullscreen=False)

        Game.game_clock = pygame.time.Clock()

    @classmethod
    def record_loop_time(cls):
        cls.loop_start = time.time()

    @classmethod
    def past_loop_time(cls):
        """Check if game loop needs to exit to keep up framerate"""
        if time.time() - cls.loop_start > cls.loop_time/2:
            return True
        else:
            return False

    @classmethod
    def process(cls):
        """Update game viewable current location variables"""
        cls.min_x = cls.center_x - cls.screen_width//2
        cls.max_x = cls.center_x + cls.screen_width//2
        cls.min_y = cls.center_y - cls.screen_height//2
        cls.max_y = cls.center_y + cls.screen_height//2

        cls.idx_cur = cls.center_x // cls.map_size
        cls.idy_cur = cls.center_y // cls.map_size



def main(seed=None):
    """Main game loop"""

    game = Game()

    game.win.font = pygame.font.Font(os.path.join('fonts', 'DejaVuSerif.ttf'), 12)
    pygame.display.set_caption('Caves')
    game.win.autowindowupdate = False
    game.win.autoupdate = False

    Game.record_loop_time()
    Game.process()

    box_width = 40
    text = "Loading ..."
    box = pygcurse.PygcurseTextbox(Game.win, (Game.screen_width//2 - box_width//2, Game.screen_width//2 - box_width//2, box_width, box_width//2), text = text , fgcolor='white' , marginleft=box_width//2 - len(text)//2 - 1, margintop=box_width//4-2)
    box.update()

    player = Player()
    world = World(seed)
    start_block = world.get(game.idx_cur, game.idy_cur)
    start_block.objects.append(player)

    elapsed = 0
    while True:
        Game.record_loop_time()
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            player.process_input(event)
        # Order is important since world modifies current view 
        # And game updates the relevant view variables
        world.process()
        Game.process()

        # ------- Draw -------
        world.draw()
        if Game.debug:
            Game.win.putchars(str(elapsed), 0, 0, 'red')
            Game.win.putchars("blocks: {}".format(len(world.blocks)), 0, 1, 'red')
            Game.win.putchars("block: ({},{})".format(game.idx_cur, game.idy_cur), 0, 2, 'red')
            Game.win.putchars("center: ({}x{})".format(game.center_x, game.center_y), 0, 3, 'red')
            Game.win.putchars("player: ({}x{})".format(player.x, player.y), 0, 4, 'red')
            spent_time = time.time() - Game.loop_start
            Game.win.putchars("spent_time: ({})".format(spent_time), 0, 5, 'red')
            Game.win.putchars("spare_time: ({})".format(1/Game.fps - spent_time), 0, 6, 'red')
        Game.win.update()
        pygame.display.update()

        # Sleep
        elapsed = game.game_clock.tick(Game.fps)

def debug(my_locals):
    pass

def parse_main():
    """Parse arguments before calling main"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--seed', help="world seed")
    args = parser.parse_args()


    if args.seed:
        main(int(args.seed))
    else:
        main()

if __name__ == "__main__":
    parse_main()
