"""Handles serialization / creating of objects from game saves"""
import shelve
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

    def save_block(self, block):
        """Save tiles/objects for block"""
        block_name = "block%d,%d" % (block.idx, block.idy)
        block_path = os.path.join(self.serial_path, block_name)
        # apparently context manager causes 50ms delay
        block_sh  = shelve.open(block_path)

        save_turn = block.world.turn if block.save_turn is None else block.save_turn
        self.remove_references(block)
        block_sh['tiles'] = block.tiles
        block_sh['entities'] = block.entities
        block_sh['hidden_map'] = block.hidden_map
        block_sh['obstacle_map'] = block.obstacle_map
        block_sh['save_turn'] = save_turn

        block_sh.close()

    def remove_references(self, blk):
        for entity in blk.entity_list:
            entity.cur_block = None
        blk.world = None

    def add_references(self, blk):
        for entity in blk.entity_list:
            entity.cur_block = blk

    def is_block(self, idx, idy):
        block_name = "block%d,%d" % (idx, idy)
        block_path = os.path.join(self.serial_path, block_name)
        return os.path.exists(block_path)

    def load_block(self, idx, idy, world):
        """Load tiles/objects and generate block object"""
        block_name = "block%d,%d" % (idx, idy)
        block_path = os.path.join(self.serial_path, block_name)
        block_sh  = shelve.open(block_path)
        block = Block(idx, idy, world=world, tiles=block_sh['tiles'],
                      entities=block_sh['entities'],
                      hidden_map=block_sh['hidden_map'],
                      obstacle_map=block_sh['obstacle_map'],
                      load_turn=world.turn)
        self.add_references(block)
        save_turn = block_sh['save_turn']
        # TODO use turndelta maybe
        turn_delta = world.turn - save_turn
        block.turn_delta = turn_delta
        block_sh.close()

        return block

    def save_settings(self, player, world):
        """Save Game state, player info"""
        #if not self.lock_exists():
        #    log.debug("Something when wrong. lock still present")
        #self.remove_lock()

        seed_str = world.seed_str
        seed_float = world.seed_float
        turn = world.turn
        logging.info("saving settings")
        path = os.path.join(self.serial_path, "settings")
        with closing(shelve.open(path)) as settings_sh:
            #settings_sh['player'] = player
            settings_sh['player_x'] = player.x
            settings_sh['player_y'] = player.y
            settings_sh['player_index'] = (world.blocks[(player.cur_block.idx, player.cur_block.idy)]
                                           .entities[player.x][player.y].index(player))
            settings_sh['view_x'] = Game.view_x
            settings_sh['view_y'] = Game.view_y
            settings_sh['turn'] = turn
            settings_sh['seed_str'] = seed_str
            settings_sh['seed_float'] = seed_float
            logging.info('turn save %d', turn)

    def has_settings(self):
        path = os.path.join(self.serial_path, "settings")
        return os.path.exists(path)
    def load_settings(self):
        """load Game state, player info into dict"""

        path = os.path.join(self.serial_path, "settings")
        ret_obj = {'player': None, 'game': None}
        if not os.path.exists(path):
            return ret_obj

        #if self.lock_exists():
        #    raise RuntimeError("Save %s did not save correctly or is already open" % self.serial_path)
        #self.set_lock()

        with closing(shelve.open(path)) as settings_sh:
            ret_obj['player_x'] = settings_sh['player_x']
            ret_obj['player_y'] = settings_sh['player_y']
            ret_obj['player_index'] = settings_sh['player_index']
            Game.view_x = settings_sh['view_x']
            Game.view_y = settings_sh['view_y'] 
            Game.update_view()
            ret_obj['turn'] = settings_sh.get('turn', 0)
            ret_obj['seed_str'] = settings_sh.get('seed_str', None)
            ret_obj['seed_float'] = settings_sh['seed_float']
            logging.info('turn load %d', settings_sh.get('turn'))
        self.settings = ret_obj
        return ret_obj

    def init_world(self):
        seed = self.settings['seed_str']
        block_seed = self.settings['seed_float']
        world = World(self, seed_str=seed, block_seed=block_seed)
        if self.settings.get('turn'):
            world.turn = self.settings['turn']
        return world

    def init_player(self, world):
        player_x = self.settings['player_x']
        player_y = self.settings['player_y']
        player_index = self.settings['player_index']
        cur_block = world.get(Game.idx_cur, Game.idy_cur)
        player = cur_block.entities[player_x][player_y][player_index]
        player.cur_block  = cur_block
        log.info("Player loaded %r block", player)
        player.register_actions()
        return player

    def save_game(self, world, player):
        self.save_settings(player, world)
        world.save_memory_blocks()
        logging.debug("saving seed {} at world turn {}".format(world.seed_float, world.turn))

    def delete_save(self):
        """Permadeath"""
        shutil.rmtree(self.serial_path)

    def init_lock(self):
        self.lock = os.path.join(self.serial_path, 'lock')

    def set_lock(self):
        open(self.lock, 'a').close()

    def lock_exists(self):
        return os.path.exists(self.lock)

    def remove_lock(self):
        os.remove(self.lock)
