"""Main game loop"""
import time
import logging
import textwrap
import random
import os

from . import libtcodpy as libtcod
import draw_text

# Optimizations through ctypes / bypassing libtcodpy
from .libtcodpy import _lib
from ctypes import c_int, byref
console_flush = _lib.TCOD_console_flush
console_clear = _lib.TCOD_console_clear
console_blit = _lib.TCOD_console_blit
sys_check_for_event = _lib.TCOD_sys_check_for_event

from . import mouse_handler
from . import status_handler
from . import actions
from . import cave_debug
from .game import Game
from .serializer import Serializer
from .world import World
from .entities import Player
from .actions import PlayerAction
from .util import game_path

log = logging.getLogger(__name__)

def run(args, game):
    """Main game loop"""
    global cur_turn
    # Setup variables used in player/world
    Game.record_loop_time()

    # Try to load save if available
    a_serializer = Serializer(args.selected_path)
    settings_obj = a_serializer.load_settings()
    if a_serializer.has_settings():
        world = a_serializer.init_world()
        world.current_block_init()
        player = a_serializer.init_player(world)
    else:
        # First time start
        world = World(a_serializer, seed_str=args.seed, block_seed=args.block_seed)
        start_block = world.get(Game.idx_cur, Game.idy_cur)
        player = start_block.set_entity(Player, Game.map_size//2, Game.map_size//2)
        start_block.reposition_entity(player, avoid_hidden=True)
        player.update_view_location()
        # Process to initalize object behavior
        # object process only works once per turn to stop multiple actions
        #world.process()
        # Remove cascade of loaded blocks due to
        # object generation moving over borders
        world.cull_old_blocks(force_cull=True)
    # Get save information / Generate initial objects

    # Draw first frame before player moves
    world.draw(init_draw=True)

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
        player.player_move(world)
        if player.is_dead:
            return_message['dead'] = True
            return_message['save'] = False
            break
        # TODO, allow FPS separate from movement(multi-turn movement)
        if player.moved:
            log.info("------------- turn %d -----------", world.turn)
            world.process()
            player.update_view_location()
            console_clear(Game.game_con)
            world.draw()
        if Game.redraw_consoles:
            libtcod.console_clear(0)
            player.update_view_location()
            world.draw()
            t = time.time()
            tt = True
            Game.redraw_consoles = False
            if Game.sidebar_enabled:
                Game.redraw_sidebar = True

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
            cave_debug.debug_print(fps_base=fps_base, world=world, game=game, player=player, spent_time=spent_time)
        mouse.conditional_print()
        game.blit_consoles(status_bar)
        console_flush()
        if player.moved or Game.redraw_consoles:
            libtcod.console_set_dirty(Game.game_width, 0, (Game.screen_width - Game.game_width), Game.screen_height)
        cur_turn = world.turn
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
        a_serializer.save_game(world, player)
    elif return_message['dead']:
        a_serializer.delete_save()
        # Reset movement keys -- bad idea to use static list
        # Register into list instance
        # TODO fix
        actions.PlayerAction.current_actions = []

    return return_message

last_game_turn = 0
cur_turn = 0
draw_text.init_ttf(game_path(os.path.join("fonts", os.path.join("pt", "PTF75F.ttf"))))
def custom_text(surface):
    global last_game_turn
    if last_game_turn > cur_turn and not Game.redraw_sidebar:
        return
    if not Game.sidebar_enabled:
        return
    s="Now that's what i call text." * 100
    s += "Turn {cur_turn}".format(cur_turn=cur_turn)
    wrapped_text = textwrap.wrap(s, 80)

    color = (255,255,255)
    tile_size = 16
    sidebar_start_loc = (Game.game_width) * tile_size + 3
    y_px_loc = 0
    for line in wrapped_text:
        draw_text.draw_text(line, surface, sidebar_start_loc, y_px_loc, color=color)
        y_px_loc += 16
    #libtcod.console_set_dirty(Game.game_width, 0, Game.game_width - Game.screen_width, Game.game_height)
    #libtcod.console_set_dirty(sidebar_start_loc, y_px_loc + tile_size, 30 * 16, len(line) * 16)
    if Game.redraw_sidebar:
        Game.redraw_sidebar = False
    else:
        last_game_turn += 1
libtcod.sys_register_SDL_renderer(custom_text)
