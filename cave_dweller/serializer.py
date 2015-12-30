import shelve
import os
import logging
import shutil
from contextlib import closing

from util import game_path
from block import Block
from game import Game

log = logging.getLogger(__name__)

class Serializer(object):
    """Serialize objects into save
       TODO: make folder name separate from seed"""

    def __init__(self, folder=None):
        if not os.path.exists(game_path('data')):
            os.mkdir(game_path('data'))


        # Find general name for folder
        if not folder:
            num = 1
            dir_prefix = "world"
            while True:
                folder_name = '_'.join([dir_prefix, str(num)])
                self.serial_path = os.path.join(game_path('data'), folder_name)
                if not os.path.exists(self.serial_path):
                    os.mkdir(self.serial_path)
                    break
                num += 1
            self.init_lock()
            self.set_lock()
        else:
            self.serial_path = os.path.join(game_path('data'), folder)
            if not os.path.exists(self.serial_path):
                raise RuntimeError("Given folder %s does not exist" %
                                   self.serial_path)
            self.init_lock()

    def save_block(self, block):
        """Save tiles/objects for block"""
        block_name = "block%d,%d" % (block.idx, block.idy)
        block_path = os.path.join(self.serial_path, block_name)
        with closing(shelve.open(block_path)) as block_sh:
            block_sh['tiles'] = block.tiles
            block_sh['entities'] = block.entities
            block_sh['hidden_map'] = block.hidden_map
            block_sh['obstacle_map'] = block.obstacle_map
            save_turn = block.world.turn if block.save_turn is None else block.save_turn
            block_sh['save_turn'] = save_turn

    def is_block(self, idx, idy):
        block_name = "block%d,%d" % (idx, idy)
        block_path = os.path.join(self.serial_path, block_name)
        return os.path.exists(block_path)

    def load_block(self, idx, idy, world):
        """Load tiles/objects and generate block object"""
        block_name = "block%d,%d" % (idx, idy)
        block_path = os.path.join(self.serial_path, block_name)
        with closing(shelve.open(block_path)) as block_sh: 
            block = Block(idx, idy, world=world, tiles=block_sh['tiles'],
                          entities=block_sh['entities'],
                          hidden_map=block_sh['hidden_map'],
                          obstacle_map=block_sh['obstacle_map'],
                          load_turn=world.turn)

            save_turn = block_sh['save_turn']
            # TODO use turndelta maybe
            turn_delta = world.turn - save_turn
            block.turn_delta = turn_delta

        return block

    def save_settings(self, player, world):
        """Save Game state, player info"""
        if not self.lock_exists():
            log.debug("Something when wrong. lock still present")
        self.remove_lock()

        seed = world.rand_seed
        turn = world.turn
        logging.info("saving settings")
        path = os.path.join(self.serial_path, "settings")
        with closing(shelve.open(path)) as settings_sh:
            #settings_sh['player'] = player
            settings_sh['player_x'] = player.x
            settings_sh['player_y'] = player.y
            settings_sh['player_index'] = (world.blocks[(Game.idx_cur, Game.idy_cur)]
                                           .entities[player.x][player.y].index(player))
            settings_sh['view_x'] = Game.view_x
            settings_sh['view_y'] = Game.view_y
            settings_sh['turn'] = turn
            settings_sh['seed'] = seed
            logging.info('turn save %d', turn)

    def load_settings(self):
        """load Game state, player info into dict"""

        path = os.path.join(self.serial_path, "settings")
        ret_obj = {'player': None, 'game': None}
        if not os.path.exists(path):
            return ret_obj

        if self.lock_exists():
            raise RuntimeError("Save %s did not save correctly or is already open" % self.serial_path)
        self.set_lock()

        with closing(shelve.open(path)) as settings_sh:
            ret_obj['player_x'] = settings_sh['player_x']
            ret_obj['player_y'] = settings_sh['player_y']
            ret_obj['player_index'] = settings_sh['player_index']
            Game.view_x = settings_sh['view_x']
            Game.view_y = settings_sh['view_y'] 
            Game.update_view()
            ret_obj['turn'] = settings_sh.get('turn', 0)
            ret_obj['seed'] = settings_sh.get('seed', None)
            logging.info('turn load %d', settings_sh.get('turn'))
        return ret_obj

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
