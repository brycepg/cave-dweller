import os
import unittest
import random
import time
import operator
import math
import operator
import copy
import itertools
import sys
import collections
import shutil

import libtcodpy as libtcod

import entities
import actions
import gen_map
import tiles
from world import World
from block import Block, DuplicateBlockError
from game import Game
from entities import Player, Entity
from tiles import Id
import hidden_map_handler
from gen_map import generate_obstacle_map
from gen_map import gen_map as generate_map
import serializer
import util

#def test_save_game(benchmark):
#    basedir=util.game_path('test_data_dir')
#    s = serializer.Serializer(basedir=basedir)
#    folder = s.folder_name
#    w = World(s, block_seed=0)
#    b = w.get(0,0)
#    p = b.set_entity(entities.Player, 3, 7)
#    p_x, p_y = p.x, p.y
#    turn = w.turn
#    benchmark.pedantic(s.save_game, args=(w,p), rounds=1)
#    shutil.rmtree(s.serial_path)
#    shutil.rmtree(basedir)

def test_save_block(benchmark):
    basedir=util.game_path('test_data_dir')
    s = serializer.Serializer(basedir=basedir)
    folder = s.folder_name
    w = World(s, block_seed=0)
    b = w.get(0,0)
    p = b.set_entity(entities.Player, 3, 7)
    p_x, p_y = p.x, p.y
    turn = w.turn
    benchmark.pedantic(s.save_block, args=(b,), rounds=1)
    shutil.rmtree(s.serial_path)
    shutil.rmtree(basedir)
