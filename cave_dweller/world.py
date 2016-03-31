"""BlockManager / Container for World class"""
import random
import logging

from .tiles import Tiles
from .tiles import Id
from .block import Block
from .game import Game

log = logging.getLogger(__name__)

from . import gen_map

class GetOutOfLoop(Exception):
    """Exception used to break out of multiple for-loops"""
    pass

class World(object):
    """
    Block manager.
    Holds all blocks. Updates and draws world
    """
    def __init__(self, a_serializer, seed_str=None, block_seed=None):
        """TODO, make seed separate from timestamp"""
        self.seed_str, self.seed_float = self.generate_seeds(seed_str, block_seed)
        #self.block_generator = gen_map.BlockGenerator(self.perlin_seed)
        log.info("Seed string: %s", self.seed_str)
        log.info("Block seed: %d", self.seed_float)
        self.a_serializer = a_serializer
        self.blocks = {}
        self.inactive_blocks = {}
        self.turn = 0

    def __getitem__(self, key):
        return self.blocks[(key)]

    def generate_seeds(self, seed_str=None, seed_float=None):
        """Hash seed str to generate seed int for noise function

        If neither provided, use random int

        If seed int is provided from command-line, use that(no seed str)
        """
        if seed_str is None and seed_float is None:
            # snoise starts acting weird at at higher values...
            seed_float = random.randrange(-65536, 65536)
        elif seed_str is not None and seed_float is None:
            seed_float = gen_map.string_seed(seed_str)
        elif seed_float is not None:
            seed_float = seed_float
        random.seed(float(seed_float))
        return seed_str, float(seed_float)

    def inspect(self, abs_x, abs_y):
        """Inspect tile for a description of current tiles/entity"""
        #TODO should be offloaded somewhere else?
        idx = abs_x // Game.map_size
        idy = abs_y // Game.map_size
        x = abs_x % Game.map_size
        y = abs_y % Game.map_size
        block = self.get(idx, idy)
        obj = block.get_entity(x, y)
        if block.hidden_map[x][y] is True:
            return None
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
        for block in self.blocks.values():
            if (abs(Game.idx_cur - block.idx) > loaded_block_radius or
                    abs(Game.idy_cur - block.idy) > loaded_block_radius):
                if force_cull or (self.turn - block.load_turn) > 10 or past_limit:
                    block.save_turn = self.turn
                    self.inactive_blocks[(block.idx, block.idy)] = \
                            self.blocks.pop((block.idx, block.idy))

        try:
            for block in self.inactive_blocks.values():
                if self.turn - block.save_turn  > 10000:
                    self.a_serializer.save_block(block)
                    del self.inactive_blocks[(block.idx, block.idy)]
                    if Game.past_loop_time() and not force_cull:
                        raise GetOutOfLoop
        except GetOutOfLoop:
            log.debug("serialization timeout")

    def current_block_init(self):
        """Load current block for start of game"""
        # Load current block first
        if not (Game.idx_cur, Game.idy_cur) in self.blocks:
            self.blocks[(Game.idx_cur, Game.idy_cur)] = self.load_block(Game.idx_cur, Game.idy_cur)


    def load_surrounding_blocks(self, idx_cur, idy_cur,
                                loaded_block_radius=Game.loaded_block_radius,
                                ignore_time=True):
        """Loads blocks around the point (idx_cur, idy_cur)
        in a square grid whose width/height
        is specified by loaded_block_radius

        ignore_time
            if false uses game time to determine if the loop needs to exit
        """
        try:
            # Load blocks in a square 'radius' around player
            for idy in range(idy_cur - Game.loaded_block_radius,
                             idy_cur + loaded_block_radius + 1):
                for idx in range(idx_cur - loaded_block_radius,
                                 idx_cur + loaded_block_radius + 1):
                    if not (idx, idy) in self.blocks:
                        self.blocks[(idx, idy)] = self.load_block(idx, idy)
                        if not ignore_time and Game.past_loop_time():
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
        elif (idx, idy) in self.inactive_blocks:
            block = self.inactive_blocks.pop((idx, idy))
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
        if (idx, idy) in self.inactive_blocks:
            block = self.inactive_blocks.pop((idx, idy))
        elif self.a_serializer.is_block(idx, idy):
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
        self.turn += 1

    def draw(self, init_draw=False):
        """Call viewable block's draw function"""
        # Draw at max 4 blocks
        # (Assumption that the viewing size is smaller than the map_size
        #log.info("---- turn ---- %d", self.turn)
        sample_locations = [(Game.min_x // Game.map_size, Game.min_y // Game.map_size),
                            (Game.min_x // Game.map_size, Game.max_y  // Game.map_size),
                            (Game.max_x // Game.map_size, Game.min_y  // Game.map_size),
                            (Game.max_x // Game.map_size, Game.max_y  // Game.map_size)]

        # Get unique block identifiers
        uniq_locs = frozenset(sample_locations)

        for loc in uniq_locs:
            #log.info("Draw %dx%d", block.idx, block.idy)
            block = self.get(*loc)
            block.draw_block()
        if init_draw:
            world.draw() # Get rid of artifacts from determining hidden map

    def get_block(self, abs_x, abs_y):
        """Get block at the absolute coordinate"""
        idx = abs_x // Game.map_size
        idy = abs_y // Game.map_size
        block = self.blocks[(idx, idy)]
        return block

    def save_memory_blocks(self):
        logging.info("Saving blocks.. bye bye")
        for block in self.blocks.values():
            self.a_serializer.save_block(block)

        for block in self.inactive_blocks.values():
            self.a_serializer.save_block(block)
