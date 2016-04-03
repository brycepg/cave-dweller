"""Startup game menu"""
import logging
import time
import os
import operator
import shutil

from . import libtcodpy as libtcod
from . import tiles

from .game import Game
from .util import game_path

class Menu(object):
    """Menus for death and intro
       They really suck. Maybe have a more general system for menus"""
    def __init__(self):
        self.enter_game = None
        self.quit = False
        self.selected_path = None
        self.background_con = libtcod.console_new(Game.screen_width, Game.screen_height)

    def enter_menu(self):
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
        menu_con = libtcod.console_new(Game.screen_width, Game.screen_height)
        cursor_pos = 0
        menu = ["New Game",
                "Load Saved Game",
                "Quit"]
        try:
            # Sort saves by date modified
            saves = os.listdir(game_path('data'))
            save_paths = []
            for save in saves[:]:
                save_path = os.path.join(game_path('data'), save)
                settings_path = os.path.join(save_path, 'settings')
                if os.path.exists(save_path):
                    save_paths.append(save_path)
            mtimes = [os.path.getmtime(save) for save in save_paths]
            my_sort = list(zip(saves, mtimes))
            my_sort.sort(key=operator.itemgetter(1), reverse=True)
            saves = [item[0] for item in my_sort]
        except OSError:
            logging.debug("data folder could not be read")
            saves = []
        past_time = 0
        menu_done = False

        current_list = menu

        x_start = Game.screen_width//2 - 8
        y_start = Game.screen_height//2-2
        while not menu_done:
            while True:
                libtcod.console_clear(0)
                libtcod.console_clear(menu_con)
                key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
                self.draw_background(x_start, y_start, current_list)
                if current_list is menu:
                    if key.vk == libtcod.KEY_ENTER:
                            # New game
                            if cursor_pos == 0:
                                menu_done = True
                                self.enter_game = True
                            # Saves
                            elif cursor_pos == 1 and len(saves) > 0:
                                current_list = saves
                                cursor_pos = 0
                                while key.vk != libtcod.KEY_NONE:
                                    key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED)
                                break
                            # Quit
                            elif cursor_pos == 2:
                                menu_done = True
                                self.enter_game = False
                                self.quit = True
                            else:
                                logging.error("Menu should not be here")
                elif current_list is saves:
                    if key.vk == libtcod.KEY_ENTER:
                        if len(saves) > 0:
                            self.selected_path = saves[cursor_pos]
                            self.enter_game = True
                            logging.info("entering {}".format(self.selected_path))
                            menu_done = True
                    if key.vk == libtcod.KEY_ESCAPE:
                        current_list = menu
                        cursor_pos = 0

                if key.vk == libtcod.KEY_NONE:
                    break
                if time.time() - past_time > .2:
                    past_time = time.time()
                    if key.vk == libtcod.KEY_UP and cursor_pos > 0:
                        cursor_pos-=1
                    if key.vk == libtcod.KEY_DOWN and cursor_pos < len(current_list)-1:
                        cursor_pos+=1

            if libtcod.console_is_window_closed():
                self.quit = True
                menu_done = True
            libtcod.console_print(menu_con, x_start, y_start, "%c%c%c%cCave Dweller%c"%(libtcod.COLCTRL_FORE_RGB,255,1,1,libtcod.COLCTRL_STOP))
            for index, item in enumerate(current_list):
                if index == 1 and current_list is menu and len(saves) == 0:
                    the_format = [55, 55, 55]
                    if cursor_pos == index:
                        the_format[0] += 30
                        the_format[1] += 30
                        the_format[2] += 30
                elif cursor_pos == index:
                    the_format = [255,255,255]
                else:
                    the_format = [155, 155, 155]
                if current_list is saves:
                    item = item.replace("_", " ").capitalize()
                libtcod.console_print(menu_con, x_start, y_start + 1 + index, "%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,the_format[0], the_format[1], the_format[2], item, libtcod.COLCTRL_STOP))

            libtcod.console_blit(self.background_con, 0, 0, 0, 0, 0, 0, 0)
            libtcod.console_blit(menu_con, 0, 0, 0, 0, 0, 0, 0, bfade=0)
            libtcod.console_flush()
            time.sleep(Game.action_interval)

    def game_over(self):
        done = False
        while not done:
            while True:
                key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED)
                if key.vk == libtcod.KEY_ENTER:
                    done = True
                if key.vk == libtcod.KEY_NONE:
                    break
                if libtcod.console_is_window_closed():
                    self.enter_game = False
                    self.quit = True
                    done = True
            msg = "You have died"
            libtcod.console_print(0, (Game.game_width-len(msg)) // 2, Game.game_height//2+1, "%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,255,1,1,msg, libtcod.COLCTRL_STOP))
            msg = "Press enter to continue"
            libtcod.console_print(0, (Game.game_width-len(msg)) // 2, Game.game_height//2+2, "%s"%(msg))
            libtcod.console_flush()

    def draw_background(self, x_start, y_start, current_list):
        # Here be dragons
        x_length = 19
        x_offset = 2

        y_offset = 1
        y_length = 6
        y_length = len(current_list) + 3


        wall = tiles.Tiles.wall
        ground = tiles.Tiles.ground

        for x in range(Game.screen_width):
            for y in range(Game.screen_height):
                libtcod.console_put_char_ex(self.background_con, x, y, ' ', wall.fg, wall.bg)
        for x in range(x_length):
            for y in range(y_length):
                libtcod.console_put_char_ex(self.background_con, x_start+x-x_offset, y_start+y-y_offset, ' ', None, ground.bg)
        for x in range(x_length-2):
            libtcod.console_put_char_ex(self.background_con, x + x_start-x_offset+1, y_start-y_offset-2, wall.char, wall.fg, wall.bg)
            libtcod.console_put_char_ex(self.background_con, x + x_start-x_offset+1, y_start-y_offset-1, ' ', None, ground.bg)
            libtcod.console_put_char_ex(self.background_con, x + x_start-x_offset+1, y_start-y_offset+y_length, ' ', None, ground.bg)
            libtcod.console_put_char_ex(self.background_con, x + x_start-x_offset+1, y_start-y_offset+y_length+1, wall.char, wall.fg, wall.bg)

        for y in range(y_length):
            libtcod.console_put_char_ex(self.background_con, x_start-x_offset-1, y+y_start-y_offset, wall.char, wall.fg, wall.bg)
            libtcod.console_put_char_ex(self.background_con, x_start-x_offset+x_length, y+y_start-y_offset, wall.char, wall.fg, wall.bg)

        libtcod.console_put_char_ex(self.background_con, x_start-x_offset, y_start-y_offset-1, wall.char, wall.fg, wall.bg)
        libtcod.console_put_char_ex(self.background_con, x_start-x_offset+x_length-1, y_start-y_offset-1, wall.char, wall.fg, wall.bg)
        libtcod.console_put_char_ex(self.background_con, x_start-x_offset+x_length-1, y_start-y_offset+y_length, wall.char, wall.fg, wall.bg)
        libtcod.console_put_char_ex(self.background_con, x_start-x_offset, y_start-y_offset+y_length, wall.char, wall.fg, wall.bg)
