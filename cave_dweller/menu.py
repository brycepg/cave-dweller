import logging
import time
import os

import libtcodpy as libtcod

from game import Game

class Menu(object):
    """Menus for death and intro
       They really suck. Maybe have a more general system for menus"""
    def __init__(self):
        self.enter_game = None
        self.quit = False
        self.selected_seed = None

    def enter_menu(self):
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
        menu_con = libtcod.console_new(Game.screen_width//2, Game.screen_height//2)
        cursor_pos = 0
        menu = ["New Game",
                "Load Saved Game",
                "Quit"]
        try:
            saves = os.listdir('data')
        except OSError:
            logging.debug("data folder could not be read")
            saves = []
        past_time = 0
        menu_done = False

        current_list = menu

        while not menu_done:
            while True:
                libtcod.console_clear(0)
                libtcod.console_clear(menu_con)
                key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
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
                            self.selected_seed = saves[cursor_pos]
                            self.enter_game = True
                            logging.info("entering {}".format(self.selected_seed))
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
            libtcod.console_print(menu_con, 0, 0, "%c%c%c%cCave Dweller%c"%(libtcod.COLCTRL_FORE_RGB,255,1,1,libtcod.COLCTRL_STOP))
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
                libtcod.console_print(menu_con, 0, index+1, "%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,the_format[0], the_format[1], the_format[2], item, libtcod.COLCTRL_STOP))
            if current_list is saves and (len(saves) == 0 or saves == ['']):
                libtcod.console_print(menu_con, 0, 1, "%c%c%c%cYou do not have any saves%c" % (libtcod.COLCTRL_FORE_RGB,255, 255, 255, libtcod.COLCTRL_STOP))

            libtcod.console_blit(menu_con, 0, 0, 0, 0, 0, Game.screen_width//2 - 10, Game.screen_height//2-2)
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
