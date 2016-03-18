import logging
import time

import libtcodpy as libtcod

# Optimizations through ctypes / bypassing libtcodpy
from libtcodpy import _lib
from ctypes import c_float, c_int, byref
console_flush = _lib.TCOD_console_flush
console_clear = _lib.TCOD_console_clear
console_blit = _lib.TCOD_console_blit
sys_check_for_event = _lib.TCOD_sys_check_for_event
ffade = c_float(1.0)
bfade = c_float(1.0)
transparent_fade = c_float(0.0)
mouse_ffade = c_float(0.75)

import mouse_handler
import status_handler
import actions
import cave_debug
from game import Game
from serializer import Serializer
from world import World
from entities import Player
from actions import PlayerAction

log = logging.getLogger(__name__)

def run(args, game):
    """Main game loop"""
    # Setup variables used in player/world
    Game.record_loop_time()

    # Try to load save if available
    a_serializer = Serializer(args.selected_path)
    settings_obj = a_serializer.load_settings()
    if settings_obj.get('seed_str') is not None:
        seed = settings_obj['seed_str']
    else:
        seed = args.seed

    if settings_obj.get('seed_float') is not None:
        block_seed = settings_obj['seed_float']
    else:
        block_seed = args.block_seed

    world = World(a_serializer, seed_str=seed, block_seed=block_seed)
    if settings_obj.get('turn'):
        world.turn = settings_obj['turn']
    # Get save information / Generate initial objects

    if settings_obj.get('player_index') is not None:
        world.current_block_init()
        player_x = settings_obj['player_x']
        player_y = settings_obj['player_y']
        player_index = settings_obj['player_index']
        cur_block = world.blocks[(Game.idx_cur, Game.idy_cur)]
        player = cur_block.entities[player_x][player_y][player_index]
        player.cur_block  = cur_block
        log.info("Player loaded %r block", player)
        player.register_actions()
    else:
        player = Player()
        start_block = world.get(Game.idx_cur, Game.idy_cur)
        start_block.entities[player.x][player.y].append(player)
        start_block.entity_list.append(player)
        start_block.reposition_entity(player, avoid_hidden=True)
        player.cur_block = start_block
        player.update_view_location()
        Game.update_view()
        # Process to initalize object behavior
        # object process only works once per turn to stop multiple actions
        world.turn = -1
        world.process()
        world.turn += 1
        # Remove cascade of loaded blocks due to
        # object generation moving over borders
        world.cull_old_blocks(force_cull=True)
    # Draw first frame before player moves
    world.draw()

    # Messages for out of game menu
    return_message = {}
    return_message['save'] = True
    return_message['dead'] = False
    return_message['quit'] = False

    # Counter for loop time

    # Process/Draw time (no limit)
    spent_time = 0
    # fps - Include flush
    fps_base = Game.fps

    skipped_loads = 0
    skipped_culls = 0

    debug_info = None

    key = libtcod.Key()
    libmouse = libtcod.Mouse()
    mouse = mouse_handler.Mouse(libmouse)
    libtcod.mouse_show_cursor(False)

    status_bar = status_handler.StatusBar()
    while True:
        Game.record_loop_time()
        if libtcod.console_is_window_closed():
            return_message['quit'] = True
            break
        # Order is important since world modifies current view
        # And game updates the relevant view variables
        player.move(world)
        if player.is_dead:
            return_message['dead'] = True
            return_message['save'] = False
            break
        # TODO, allow FPS separate from movement(multi-turn movement)
        if player.moved:
            log.info("------------- turn %d -----------", world.turn)
            world.process()
            player.update_view_location()
            world.turn += 1
            console_clear(Game.game_con)
            world.draw()
        # Load blocks during draw even if player is not doing anything
        console_clear(Game.sidebar_con)
        console_clear(Game.mouse_con)
        console_clear(status_bar.con)
        if not Game.past_loop_time() or skipped_culls > 93:
            world.cull_old_blocks()
            skipped_culls = 0
        else:
            skipped_culls += 1
            log.debug("skip cull")
        if not Game.past_loop_time() or skipped_loads > 547:
            world.load_surrounding_blocks(Game.idx_cur, Game.idy_cur,
                                          Game.loaded_block_radius,
                                          ignore_time=False)
            skipped_loads = 0
        else:
            log.debug("load timeout")
            skipped_loads += 1

        status_bar.run(player, world, mouse)
        if Game.debug:
            spent_time = (time.time() - Game.loop_start) * .1 + spent_time * .9
            cave_debug.debug_print(locals())
        mouse.conditional_print()
        console_blit(Game.game_con, 0, 0,
                             Game.game_width, Game.game_height,
                             0, 0, 0, ffade, bfade)
        status_bar.draw()
        if not debug_info and Game.sidebar_enabled:
            console_blit(Game.sidebar_con, 0, 0, 0, 0,
                                 0, Game.game_width, 0, ffade, bfade)
        console_blit(Game.debug_con, 0, 0, 0, 0,
                             0, 0, 0, ffade, transparent_fade)
        console_blit(game.mouse_con, 0, 0, 0, 0,
                             0, 0, 0, mouse_ffade, transparent_fade)
        console_flush()
        fps_base = (time.time() - Game.loop_start) * .1 + fps_base * .9
        console_clear(Game.debug_con)
        # ----- keyboard input -----
        status_bar.is_mode_set = False
        while True:
            sys_check_for_event(c_int(libtcod.EVENT_ANY), byref(key), byref(mouse.mouse))
            status_bar.get_input(key, mouse)
            if key.vk == libtcod.KEY_NONE:
                break
            #print("pressed {}".format(key.pressed))
            #print("char {}".format((chr(key.c))))
            #print("vk {}".format(key.vk))
            if Game.debug:
                debug_info = cave_debug.debug_menu(key, debug_info, world)
                if key.pressed and key.lctrl and key.c == ord('f'):
                    if Game.action_interval:
                        Game.action_interval = 0
                        Game.move_per_sec = 0
                        libtcod.sys_set_fps(0)
                        log.info("Fast")
                    else:
                        log.info("Normal")
                        Game.action_interval = Game.default_action_interval
                        libtcod.sys_set_fps(Game.default_fps)
                        Game.move_per_sec = 3/4 * Game.default_action_interval
                        Game.action_interval = Game.default_action_interval
            player.process_input(key)
            game.get_game_input(key)
        mouse.update_coords()

    if return_message['save']:
        world.save_memory_blocks()
        logging.debug("saving seed {} at world turn {}".format(world.seed_int, world.turn))
        world.a_serializer.save_settings(player, world)
    elif return_message['dead']:
        world.a_serializer.delete_save()
        # Reset movement keys -- bad idea to use static list
        # Register into list instance
        # TODO fix
        actions.PlayerAction.current_actions = []

    return return_message
