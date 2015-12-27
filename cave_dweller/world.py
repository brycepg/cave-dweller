"""Container for World class"""
import time
import random
import re
import logging

from tiles import Tiles
from tiles import Id
from block import Block
from game import Game

log = logging.getLogger(__name__)

class GetOutOfLoop(Exception):
    """Exception used to break out of multiple for-loops"""
    pass

class World(object):
    """Holds all blocks. Updates and draws world"""
    def __init__(self, rand_seed=None):
        """TODO, make seed separate from timestamp"""
        self.rand_seed = rand_seed
        self.perlin_seed = None
        self.generate_seeds(self.rand_seed)
        self.a_serializer = None
        self.blocks = {}
        self.turn = 0

    def generate_seeds(self, rand_seed):
        """Generate time seed if not given
        Seed rand
        Generate reduced size seed for C perlin function"""
        if rand_seed is None:
            rand_seed = time.time()
        else:
            rand_seed = int(rand_seed)
        # Do not use floating point time
        rand_seed = int(rand_seed)
        log.info("seed: %d", rand_seed)

        self.rand_seed = rand_seed

        # Seed random
        random.seed(self.rand_seed)

        # Seed for perlin noise -- doesn't work with big numbers?
        # Probably due to variable size constraints in C
        self.perlin_seed = random.randrange(-65565, 65565)

    def inspect(self, abs_x, abs_y):
        idx = abs_x // Game.map_size
        idy = abs_y // Game.map_size
        x = abs_x % Game.map_size
        y = abs_y % Game.map_size
        block = self.get(idx, idy)
        obj = block.get_object(x, y)
        if obj:
            obj_name = type(obj).__name__
            # Add spaces before capital characters(except for the first)
            name_mod = ''.join(' ' + char if char.isupper() and
                               index != 0 else char for
                               index, char in enumerate(obj_name))
            return name_mod
        tile = block.get_tile(x, y)
        if tile.name:
            return tile.name
        else:
            return None
    
    def cull_old_blocks(self, force_cull=False):
        """Serialize blocks that are outside of loaded radius,
           and have been alive for more than some number of turns

           arguments:
               force_cull
                    if True, ignores how long block has been alive to cull.
                    (default avoids constant loading/deloading from
                    objects/player moving accross boundries)
           """
        # Hard-limit the number of active blocks -- only a problem in fast-mode
        HARD_LIMIT = 100
        past_limit = not (len(self.blocks) < HARD_LIMIT)

        loaded_block_radius = Game.loaded_block_radius
        try:
            for block in self.blocks.values():
                if (abs(Game.idx_cur - block.idx) > loaded_block_radius or
                        abs(Game.idy_cur - block.idy) > loaded_block_radius):
                    if force_cull or (self.turn - block.load_turn) > 10 or past_limit:
                        self.a_serializer.save_block(block)
                        del self.blocks[(block.idx, block.idy)]
                        if Game.past_loop_time() and not past_limit and not force_cull:
                            raise GetOutOfLoop
        except GetOutOfLoop:
            log.debug("cull timeout")

    def current_block_init(self):
        """Load current block for start of game"""
        # Load current block first
        if not (Game.idx_cur, Game.idy_cur) in self.blocks:
            self.blocks[(Game.idx_cur, Game.idy_cur)] = self.load_block(Game.idx_cur, Game.idy_cur)


    def load_surrounding_blocks(self):
        """Loads blocks surrounding player specified by loaded_block_radius"""
        # Do not timeout block loading at begginging(a block might not appear)

        idx_cur = Game.idx_cur
        idy_cur = Game.idy_cur

        loaded_block_radius = Game.loaded_block_radius

        try:
            # Load blocks in a square 'radius' around player
            for idy in range(idy_cur - Game.loaded_block_radius,
                             idy_cur + loaded_block_radius + 1):
                for idx in range(idx_cur - loaded_block_radius,
                                 idx_cur + loaded_block_radius + 1):
                    if not (idx, idy) in self.blocks:
                        self.blocks[(idx, idy)] = self.load_block(idx, idy)
                        if Game.past_loop_time():
                            raise GetOutOfLoop
        except GetOutOfLoop:
            pass
            #log.debug('load timeout load_surrounding_blocks')

    def get(self, idx, idy):
        """
        Tries to get a block at (idx, idy).
        If not in active blocks,
        see if it's serialized.
        If it's not serialized,
        generate it.

        Generate requested block and return reference
        Python doesn't like negative indices. use idx,idy coordinates as hash table
        Required since each block is dynamically generated
        """
        if (idx, idy) in self.blocks:
            # Load from active blocks
            block = self.blocks[(idx, idy)]
        elif self.a_serializer.is_block(idx, idy):
            # Load from disk
            block = self.a_serializer.load_block(idx, idy, self)
        else:
            # Generate block
            block = Block(idx, idy, self, load_turn=self.turn)

        # Side-effect to promote ease of use and to 
        #   stop bugs from duplicate blocks
        self.blocks[(idx, idy)] = block

        #if block.turn_delta is not None:
        #    print("Turn delta %d on %dx%d" % (block.turn_delta, idx, idy))
        #    while block.turn_delta > 0:
        #        print("Process %d" % block.turn_delta)
        #        block.turn_delta -= 1
        #        block.process()

        return block

    def load_block(self, idx, idy):
        """load without without checking active blocks or storing"""
        # Load from save
        if self.a_serializer.is_block(idx, idy):
            block = self.a_serializer.load_block(idx, idy, self)
        else:
            # Generate if not from save
            block = Block(idx, idy, self, load_turn=self.turn)
        return block

    def process(self):
        """Do game calculations
        Mainly for loading and de-loading blocks relative to the viewable area
        """
        for block in self.blocks.values():
            block.process()

        # A little hack to randomize digging tile
        Tiles.dig3.attributes['next'] = random.choice(Id.any_ground)

    def get_id_from_abs(self, abs_x, abs_y):
        """Get idx/idy from abs coord"""
        idx = abs_x // Game.map_size
        idy = abs_y // Game.map_size
        return idx, idy

    def draw(self):
        """Call viewable block's draw function"""
        # Draw at max 4 blocks
        # (Assumption that the viewing size is smaller than the map_size
        #log.info("---- turn ---- %d", self.turn)
        sample_locations = [(Game.min_x // Game.map_size, Game.min_y // Game.map_size),
                            (Game.min_x // Game.map_size, Game.max_y  // Game.map_size),
                            (Game.max_x // Game.map_size, Game.min_y  // Game.map_size),
                            (Game.max_x // Game.map_size, Game.max_y  // Game.map_size)]

        uniq_locs = frozenset(sample_locations)

        for loc in uniq_locs:
            #log.info("Draw %dx%d", block.idx, block.idy)
            block = self.get(*loc)
            block.draw()

    def get_block(self, abs_x, abs_y):
        """Get block at the absolute coordinate"""
        idx = abs_x // Game.map_size
        idy = abs_y // Game.map_size
        block = self.blocks[(idx, idy)]
        return block

    def save_active_blocks(self):
        logging.info("Saving blocks.. bye bye")
        for block in self.blocks.values():
            self.a_serializer.save_block(block)
