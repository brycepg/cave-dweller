import unittest

from cave_dweller.world import World
from cave_dweller.game import Game
from cave_dweller.entities import Player
from cave_dweller import actions

from .mocks import SerializerMock, HeadlessGame

class TestPlayer(unittest.TestCase):
    def setUp(self):
        s = SerializerMock()
        g = HeadlessGame()
        w = World(s, block_seed=0)
        start_block = w.get(0, 0)
        start_loc_x = Game.map_size//2
        start_loc_y = Game.map_size//2
        player = start_block.set_entity(Player, start_loc_x, start_loc_y)

        self.start_block = start_block
        self.player = player
        self.start_loc_x = start_loc_x
        self.start_loc_y = start_loc_y

    def test_reposition(self):
        start_block = self.start_block
        start_loc_x = self.start_loc_x
        start_loc_y = self.start_loc_y
        player = self.player

        self.assertTrue(player in start_block.entities[start_loc_x][start_loc_y])
        # Potentially update player location
        start_block.reposition_entity(player, avoid_hidden=True)
        self.assertFalse(player in start_block.entities[start_loc_x][start_loc_y])
        self.assertTrue(player in start_block.entities[player.x][player.y])
        self.assertTrue(player in start_block.entity_list)

    def test_movement(self):
        start_block = self.start_block
        player = self.player
        start_block.reposition_entity(player, avoid_hidden=True)
        player = self.player
        start_block = self.start_block
        a = actions.Move()
        old_x, old_y = player.x, player.y
        a.dir_dict['right'] = True
        a.dir('right', (old_x+1, old_y), start_block, player)
        self.assertNotEqual((old_x, old_y), (player.x, player.y))
        self.assertEqual((old_x+1, old_y), (player.x, player.y))
        self.assertTrue(player in start_block.entities[player.x][player.y])
