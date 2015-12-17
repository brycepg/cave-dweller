import shelve
import os
import logging

from util import game_path
from block import Block
from game import Game

class Serializer:
    def __init__(self, seed):
        if not os.path.exists(game_path('data')):
            os.mkdir(game_path('data'))
        self.serial_path = os.path.join(game_path('data'), str(seed))
        if not os.path.exists(self.serial_path):
            os.mkdir(self.serial_path)

    def save_block(self, block):
        block_name = "block{x},{y}".format(x=block.idx, y=block.idy)
        block_path = os.path.join(self.serial_path, block_name)
        block_sh = shelve.open(block_path)
        block_sh['tiles'] = block.tiles
        block_sh['objects'] = block.objects
        block_sh.close()

    def load_block(self, idx, idy, world):
        block_name = "block{x},{y}".format(x=idx, y=idy)
        block_path = os.path.join(self.serial_path, block_name)
        if not os.path.exists(block_path):
            return None

        block_sh = shelve.open(block_path)
        block = Block(idx, idy, world=world, tiles=block_sh['tiles'], objects=block_sh['objects'])
        return block

    def save_settings(self, player):
        logging.info("saving settings")
        path = os.path.join(self.serial_path, "settings")
        settings_sh = shelve.open(path)
        settings_sh['player'] = player
        settings_sh['center_x'] = Game.center_x
        settings_sh['center_y'] = Game.center_y
        settings_sh['turn'] = player.world.turn
        logging.info('turn save {}'.format(player.world.turn))
        settings_sh.close()

    def load_settings(self, world):
        path = os.path.join(self.serial_path, "settings")
        ret_obj = {'player': None, 'game': None}
        if not os.path.exists(path):
            return ret_obj
        settings_sh = shelve.open(path)
        ret_obj['player'] = settings_sh.get('player')
        Game.center_x = settings_sh['center_x']
        Game.center_y = settings_sh['center_y'] 
        world.turn = settings_sh.get('turn', 0)
        logging.info('turn load {}'.format(settings_sh.get('turn')))
        settings_sh.close()
        return ret_obj
