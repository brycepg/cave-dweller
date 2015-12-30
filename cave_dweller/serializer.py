import shelve
import os
import logging
import shutil

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
        block_name = "block%d,%d" % (block.idx, block.idy)
        block_path = os.path.join(self.serial_path, block_name)
        block_sh = shelve.open(block_path)
        block_sh['tiles'] = block.tiles
        block_sh['entities'] = block.entities
        block_sh['hidden_map'] = block.hidden_map
        block_sh['obstacle_map'] = block.obstacle_map
        block_sh['save_turn'] = block.world.turn
        block_sh.close()

    def is_block(self, idx, idy):
        block_name = "block%d,%d" % (idx, idy)
        block_path = os.path.join(self.serial_path, block_name)
        return os.path.exists(block_path)

    def load_block(self, idx, idy, world):
        """Load tiles/objects and generate block object"""
        block_name = "block%d,%d" % (idx, idy)
        block_path = os.path.join(self.serial_path, block_name)
        block_sh = shelve.open(block_path)
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
        seed = world.rand_seed
        turn = world.turn
        logging.info("saving settings")
        path = os.path.join(self.serial_path, "settings")
        settings_sh = shelve.open(path)
        #settings_sh['player'] = player
        settings_sh['player_x'] = player.x
        settings_sh['player_y'] = player.y
        settings_sh['player_index'] = (world.blocks[(Game.idx_cur, Game.idy_cur)]
                                       .entities[player.x][player.y].index(player))
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
        ret_obj['player_x'] = settings_sh['player_x']
        ret_obj['player_y'] = settings_sh['player_y']
        ret_obj['player_index'] = settings_sh['player_index']
        Game.view_x = settings_sh['view_x']
        Game.view_y = settings_sh['view_y'] 
        Game.update_view()
        ret_obj['turn'] = settings_sh.get('turn', 0)
        ret_obj['seed'] = settings_sh.get('seed', None)
        logging.info('turn load {}'.format(settings_sh.get('turn')))
        settings_sh.close()
        return ret_obj
    
    def delete_save(self):
        """Permadeath"""
        shutil.rmtree(self.serial_path)
