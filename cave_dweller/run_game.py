import logging
import time

import libtcodpy as libtcod

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
    if settings_obj.get('seed') is not None:
        seed = settings_obj['seed']
    else:
        seed = args.seed
    world = World(a_serializer, seed)
    if settings_obj.get('turn'):
        world.turn = settings_obj['turn']
    # Get save information / Generate initial objects

    if settings_obj.get('player_index') is not None:
        world.current_block_init()
        player_x = settings_obj['player_x']
        player_y = settings_obj['player_y']
        player_index = settings_obj['player_index']
        player = world.blocks[(Game.idx_cur, Game.idy_cur)].entities[player_x][player_y].pop(player_index)
        player.register_actions()
    else:
        player = Player()
        start_block = world.get(Game.idx_cur, Game.idy_cur)
        start_block.entities[player.x][player.y].append(player)
        start_block.reposition_entity(player)
        player.update_view_location(start_block)
        Game.update_view()
        # Process to initalize object behavior
        world.process()
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
            world.turn += 1
            libtcod.console_clear(Game.game_con)
            world.draw()
        # Load blocks during draw even if player is not doing anything
        libtcod.console_clear(Game.sidebar_con)
        libtcod.console_clear(Game.mouse_con)
        libtcod.console_clear(status_bar.con)
        if not Game.past_loop_time() or skipped_culls > 193:
            world.cull_old_blocks()
            skipped_culls = 0
        else:
            skipped_culls += 1
            #log.info("skip cull")
        if not Game.past_loop_time() or skipped_loads > 547:
            world.load_surrounding_blocks(Game.idx_cur, Game.idy_cur,
                                          Game.loaded_block_radius,
                                          ignore_time=False)
            skipped_loads = 0
        else:
            #log.info("load timeout")
            skipped_loads += 1

        status_bar.run(player, world, mouse)
        if Game.debug:
            spent_time = (time.time() - Game.loop_start) * .1 + spent_time * .9
            cave_debug.debug_print(locals())
        mouse.conditional_print()
        libtcod.console_blit(Game.game_con, x=0, y=0,
                             w=Game.game_width, h=Game.game_height,
                             dst=0, xdst=0, ydst=0)
        status_bar.draw()
        if not debug_info and Game.sidebar_enabled:
            libtcod.console_blit(Game.sidebar_con, x=0, y=0, w=0, h=0,
                                 dst=0, xdst=Game.game_width, ydst=0)
        libtcod.console_blit(Game.debug_con, x=0, y=0, w=0, h=0,
                             dst=0, xdst=0, ydst=0, ffade=1, bfade=0)
        libtcod.console_blit(Game.mouse_con, x=0, y=0, w=0, h=0,
                             dst=0, xdst=0, ydst=0, ffade=.75, bfade=.0)
        libtcod.console_flush()
        fps_base = (time.time() - Game.loop_start) * .1 + fps_base * .9
        libtcod.console_clear(Game.debug_con)
        # ----- keyboard input -----
        status_bar.is_mode_set = False
        while True:
            libtcod.sys_check_for_event(libtcod.EVENT_ANY, key, mouse.mouse)
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
        world.save_active_blocks()
        logging.debug("saving seed {} at world turn {}".format(world.rand_seed, world.turn))
        world.a_serializer.save_settings(player, world)
    elif return_message['dead']:
        world.a_serializer.delete_save()
        # Reset movement keys -- bad idea to use static list
        # Register into list instance
        # TODO fix
        actions.PlayerAction.current_actions = []

    return return_message
