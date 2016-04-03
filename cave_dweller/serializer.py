"""Handles serialization / creating of objects from game saves"""
import sqlite3
from sqlite3 import Binary
import cPickle as pickle
from cPickle import dumps


import os
import logging
import shutil
from contextlib import closing

from .util import game_path
from .block import Block
from .game import Game
from .world import World

log = logging.getLogger(__name__)

class Serializer(object):
    """Serialize objects into save
       TODO: make folder name separate from seed"""

    def __init__(self, folder=None, basedir=game_path('data')):
        if not os.path.exists(basedir):
            os.mkdir(basedir)


        # Find general name for folder
        self.serial_path = None
        self.folder_name = None
        self.basedir = basedir
        self.settings = None
        self.db_path = ""
        self.connection = None

        if not folder:
            num = 1
            dir_prefix = "world"
            while True:
                folder_name = '_'.join([dir_prefix, str(num)])
                self.serial_path = os.path.join(basedir, folder_name)
                if not os.path.exists(self.serial_path):
                    os.mkdir(self.serial_path)
                    break
                num += 1
            self.folder_name = folder_name
            self.init_lock()
            self.set_lock()
        else:
            self.folder_name = folder
            self.serial_path = os.path.join(basedir, folder)
            if not os.path.exists(self.serial_path):
                raise RuntimeError("Given folder %s does not exist" %
                                   self.serial_path)
            self.init_lock()
        self.db_path = os.path.join(self.serial_path, "{name}.db".format(name=self.folder_name))
        self.connection = sqlite3.connect(self.db_path, isolation_level="DEFERRED")
        # Optimization - trade off reliability for speed increase
        self.connection.execute("PRAGMA synchronous = OFF")
        self.connection.execute("PRAGMA journal = OFF")
        self.connection.execute("CREATE table IF NOT EXISTS blocks (loc TEXT PRIMARY KEY NOT NULL, block BLOB)")
        self.connection.execute("CREATE table IF NOT EXISTS settings (key TEXT PRIMARY KEY, setting BLOB)")
        self.connection.commit()

    def save_block(self, block):
        """Save tiles/objects for block"""
        block.save_turn = block.world.turn
        # Do not save multiple world copies - my nightmare
        block.world = None
        loc = pickle.dumps((block.idx, block.idy),)
        block = sqlite3.Binary(pickle.dumps(block))
        self.connection.execute("replace into blocks values (?,?)", (loc, block))
        self.connection.commit()

    def is_block(self, idx, idy):
        """Check if block in database via block coordinates
        arguments:
            idx, idy - int coordinates
        returns:
            boolean value - true if block is in database
        """
        key = pickle.dumps((idx, idy))
        exists = self.connection.execute("SELECT 1 FROM blocks WHERE loc=? LIMIT 1",
                                         (key,)).fetchone()
        return exists is not None

    def load_block(self, idx, idy, world):
        """Load tiles/objects and generate block object"""
        key = pickle.dumps((idx, idy))
        block_bin = self.connection.execute("SELECT block FROM blocks WHERE loc=? LIMIT 1",
                                            (key,)).fetchone()
        block = pickle.loads(bytes(block_bin[0]))
        # Put world reference back on block after removing before pickle
        block.world = world
        turn_delta = world.turn - block.save_turn
        block.turn_delta = turn_delta
        return block

    def save_settings(self, world, player):
        """
        Save Game state, player info
        This should be called before serializing/freeing blocks
        """
        if not self.lock_exists():
            log.debug("Something when wrong. lock still present")
        else:
            self.remove_lock()

        seed_str = world.seed_str
        seed_float = world.seed_float
        turn = world.turn
        logging.info("saving settings")
        path = os.path.join(self.serial_path, "settings")
        settings_tup = (('player_x', player.x),
                        ('player_y', player.y),
                        ('player_idx', player.cur_block.idx),
                        ('player_idy', player.cur_block.idy),
                        ('player_index',
                         # Get the index of the cell from the bock that the player currently
                         #  resides in.
                         (world.blocks[(player.cur_block.idx, player.cur_block.idy)].
                          entities[player.x][player.y].index(player))),
                        ('turn', turn),
                        ('seed_str', seed_str),
                        ('seed_float', seed_float),)
        self.connection.executemany("REPLACE INTO settings VALUES (?,?)", settings_tup)
        self.connection.commit()
        logging.info('turn save %d', turn)

    def has_settings(self):
        """
        Check if the settings table is populated

        return: bool
        """
        # Check if settings table is populated
        exists = self.connection.execute("SELECT 1 FROM settings LIMIT 1").fetchone()
        return exists is not None
    def load_settings(self):
        """load Game state, player info into dict"""

        settings_list = self.connection.execute("SELECT * from settings").fetchall()
        settings_dict = {key: value for key, value in settings_list}
        self.settings = settings_dict
        return settings_dict

    def init_world(self):
        """
        Initialize world object from save

        Requires load_settings() to be called first, otherwise
        a KeyError will be thrown below

        returns a newly instantiated world object
        """
        seed = self.settings['seed_str']
        block_seed = self.settings['seed_float']
        world = World(self, seed_str=seed, block_seed=block_seed)
        world.turn = self.settings['turn']
        return world

    def init_player(self, world):
        """
        Initialize player object from save

        Requires load_settings() to be called first, otherwise
        a KeyError exception will be thrown below.

        Should be called after init_world since world is a required argumnet

        returns a newly instantiated player object
        """
        settings = self.settings
        player_x = settings['player_x']
        player_y = settings['player_y']
        player_index = settings['player_index']
        cur_block = world.get(settings['player_idx'], settings['player_idy'])
        player = cur_block.entities[player_x][player_y][player_index]
        log.info("Player loaded %r block", player)
        player.register_actions()
        return player

    def save_game(self, world, player):
        """
        Save settings, blocks to disk
        """
        self.save_settings(world, player)
        logging.info("Saving blocks.. bye bye")

        in_memory_blocks = world.blocks.values() + world.inactive_blocks.values()
        pickle_rows = []
        world_turn = world.turn
        for block in in_memory_blocks:
            block.save_turn = world_turn
            # Do not save multiple world copies - my nightmare
            block.world = None
            loc = dumps((block.idx, block.idy),)
            bin_block = Binary(pickle.dumps(block))
            pickle_rows.append((loc, bin_block))
            # Re-add world in case block is used again
            block.world = world

        self.connection.execute("BEGIN TRANSACTION")
        self.connection.executemany("replace into blocks values (?,?)", pickle_rows)
        self.connection.commit()
    def close_connection(self):
        """Close database/game save connection"""
        self.connection.close()

    def delete_save(self):
        """Permadeath"""
        self.connection.close()
        shutil.rmtree(self.serial_path)

    # These implement a file lock to determine if the game was saved properly
    def init_lock(self):
        self.lock = os.path.join(self.serial_path, 'lock')

    def set_lock(self):
        open(self.lock, 'a').close()

    def lock_exists(self):
        return os.path.exists(self.lock)

    def remove_lock(self):
        os.remove(self.lock)
