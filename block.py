"""container for Block"""

import math

from gen_map import generate_map_slice
from gen_map import generate_map_slice_abs_min
from gen_map import generate_map_slice_abs_more
from game import Game

WALL = 'x'
GROUND = '-'
HIDDEN = ' '


class Block:
    """Segment of world populated by object and terrain"""
    def __init__(self, idx, idy, world):
        #self.delay_generation = False if len(world.blocks) <= 1 else True
        self.delay_generation = False
        self.world = world
        self.chars = []
        self.obstacles = []
        self.objects = []
        self.idx = idx
        self.idy = idy

        self.completely_generated = False
        self.y_coord_gen_num = 0
        self.init_map_slices()


    def within_bounds(self, x, y):
        if 0 <= x < Game.map_size and 0 <= y < Game.map_size:
            return True
        else:
            return False
    def is_obstacle(self, x, y, generate_new_blocks=False):
        obstacle = None
        if self.within_bounds(x, y):
            return self.obstacles[y][x]
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            if generate_new_blocks:
                blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
                if not blk.completely_generated:
                    raise NotImplementedError("Implement stalling behavior")
            else:
                try:
                    blk = self.world.blocks[(self.idx + idx_mod, self.idy + idy_mod)]
                    print("check block {}x{}".format(blk.idx, blk.idy))
                except KeyError:
                    obstacle = True
            if obstacle is None:
                new_x = x % Game.map_size
                new_y = y % Game.map_size
                obstacle = blk.obstacles[new_y][new_x]
            return obstacle

    def get_char(self, x, y, generate_new_blocks=False):
        char = None
        if self.within_bounds(x, y):
            return self.chars[y][x]
        else:
            idx_mod = x // Game.map_size
            idy_mod = y // Game.map_size
            if generate_new_blocks:
                blk = self.world.get(self.idx + idx_mod, self.idy + idy_mod)
            else:
                try:
                    blk = self.world.blocks[(self.idx + idx_mod, self.idy + idy_mod)]
                except KeyError:
                    char = ''
            if char is None:
                new_x = x % Game.map_size
                new_y = y % Game.map_size
                char = blk.chars[new_y][new_x]
            return char

    def init_map_slices(self):
        """Generate block in 'slices' to allow a
            'timeout' after a certain threshold
             To allow other parts of the game to update."""
        while not Game.past_loop_time() or not self.delay_generation:
            #print(self.world.perlin_seed)
            num_map_slice = generate_map_slice_abs_more(self.world.perlin_seed,
                                               self.idx,
                                               self.idy,
                                               self.y_coord_gen_num,
                                               map_size=Game.map_size)
            char_line = []
            obstacle_line = []

            for val in num_map_slice:
                if val == 255:
                    char_line.append(WALL)
                    obstacle_line.append(True)
                else:
                    char_line.append(GROUND)
                    obstacle_line.append(False)
            self.chars.append(char_line)
            self.obstacles.append(obstacle_line)
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
                new_block = Block(self.idx+ (a_object.x//Game.map_size), self.idy + (a_object.y//Game.map_size), self.world)
                a_object.x = a_object.x % Game.map_size
                a_object.y = a_object.y % Game.map_size
#               if a_object.x >= Game.map_size:
#                   new_block = Block(self.idx+1, self.idy, self.world)
#                   a_object.x = a_object.x % Game.map_size
#               elif a_object.x < 0:
#                   new_block = Block(self.idx-1, self.idy, self.world)
#                   a_object.x = Game.map_size + a_object.x
#               elif a_object.y >= Game.map_size:
#                   new_block = Block(self.idx, self.idy+1, self.world)
#                   a_object.y = a_object.y % Game.map_size
#               elif a_object.y < 0:
#                   new_block = Block(self.idx, self.idy-1, self.world)
#                   a_object.y = Game.map_size + a_object.y
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
                    cur_char = self.chars[row][column]
                    if cur_char == WALL:
                        right = self.get_char(column+1, row)
                        left = self.get_char(column-1, row)
                        down = self.get_char(column, row+1)
                        up = self.get_char(column, row-1)
                        #print("{} {} {} {}".format(right, left, down, up))
                        if((right == WALL or right == HIDDEN) and
                           (left == WALL or left == HIDDEN) and
                           (up == WALL or up == HIDDEN) and
                           (down == WALL or down == HIDDEN)):
                            self.chars[row][column] = HIDDEN
                    if self.obstacles[row][column]:
                        fg = 'white'
                        bg = 'gray'
                    else:
                        fg = 'gray'
                        bg = 'black'
                    #print('{}x{}'.format(abs_x, abs_y), end=",")
                    Game.win.putchar(self.chars[row][column],
                            abs_x - Game.center_x + Game.screen_width//2,
                            abs_y - Game.center_y + Game.screen_height//2, fg, bg)
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
                                  Game.screen_height//2), a_object.fg, a_object.bg)
