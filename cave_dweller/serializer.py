import shelve
import os
import logging
import shutil

from util import game_path
from block import Block
from game import Game

class Serializer(object):
    """Serialize objects into save
       TODO: make folder name separate from seed"""

    def __init__(self, folder=None):
        if not os.path.exists(game_path('data')):
            os.mkdir(game_path('data'))

        # Find general name for folder
        #import pdb; pdb.set_trace()
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
        else:
            self.serial_path = os.path.join(game_path('data'), folder)



    def save_block(self, block):
        """Save tiles/objects for block"""
        block_name = "block{x},{y}".format(x=block.idx, y=block.idy)
        block_path = os.path.join(self.serial_path, block_name)
        block_sh = shelve.open(block_path)
        block_sh['tiles'] = block.tiles
        block_sh['objects'] = block.objects
        block_sh.close()

    def load_block(self, idx, idy, world):
        """Load tiles/objects and generate block object"""
        block_name = "block{x},{y}".format(x=idx, y=idy)
        block_path = os.path.join(self.serial_path, block_name)
        if not os.path.exists(block_path):
            return None

        block_sh = shelve.open(block_path)
        block = Block(idx, idy, world=world, tiles=block_sh['tiles'], objects=block_sh['objects'], load_turn=world.turn)
        return block

    def save_settings(self, player, world):
        """Save Game state, player info"""
        seed = world.rand_seed
        turn = world.turn
        logging.info("saving settings")
        path = os.path.join(self.serial_path, "settings")
        settings_sh = shelve.open(path)
        #settings_sh['player'] = player
        settings_sh['player_index'] = world.blocks[(Game.idx_cur, Game.idy_cur)].objects.index(player)
        settings_sh['view_x'] = Game.view_x
        settings_sh['view_y'] = Game.view_y
        settings_sh['turn'] = turn
        settings_sh['seed'] = seed
        logging.info('turn save {}'.format(turn))
        settings_sh.close()

    def load_settings(self):
        """load Game state, player info into dict"""
        path = os.path.join(self.serial_path, "settings")
        ret_obj = {'player': None, 'game': None}
        if not os.path.exists(path):
            return ret_obj
        settings_sh = shelve.open(path)
        ret_obj['player_index'] = settings_sh.get('player_index')
        Game.view_x = settings_sh['view_x']
        Game.view_y = settings_sh['view_y'] 
        ret_obj['turn'] = settings_sh.get('turn', 0)
        ret_obj['seed'] = settings_sh.get('seed', None)
        logging.info('turn load {}'.format(settings_sh.get('turn')))
        settings_sh.close()
        return ret_obj
    
    def delete_save(self):
        """Permadeath"""
        shutil.rmtree(self.serial_path)
