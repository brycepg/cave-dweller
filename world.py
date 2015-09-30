"""Container for World class"""
import time
import random

from block import Block
from game import Game

class GetOutOfLoop(Exception):
    """Exception used to break out of multiple for-loops"""
    pass

class World:
    """Holds all blocks updates and draws world"""
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
        if destroy_block is not None:
            del self.blocks[destroy_block]



    def load_surrounding_blocks(self):
        """Loads blocks surrounding player specified by loaded_block_radius"""
        # Load the current block immediately
        cur_blk = self.get(Game.idx_cur, Game.idy_cur)
        try:
            for idy in range(Game.idy_cur - self.loaded_block_radius,
                    Game.idy_cur + self.loaded_block_radius + 1):
                for idx in range(Game.idx_cur - self.loaded_block_radius,
                        Game.idx_cur + self.loaded_block_radius + 1):
                    self.get(idx, idy)
                    if Game.past_loop_time():
                        raise GetOutOfLoop
        except GetOutOfLoop:
            print('load timeout')

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
        """Do game calculations
        Mainly for loading and de-loading blocks relative to the viewable area
        """
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
