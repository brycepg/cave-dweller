import logging
import time

import libtcodpy as libtcod

from game import Game

class Menu:
    def __init__(self):
        self.enter_game = None

    def enter_menu(self):
        key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED)
        menu_con = libtcod.console_new(Game.screen_width//2, Game.screen_height//2)
        cursor_pos = 0
        menu = ["New Game",
                "Load Saved Game",
                "Quit"]
        past_time = 0
        menu_done = False
        while not menu_done:
            while True:
                key = libtcod.console_check_for_keypress(libtcod.KEY_PRESSED|libtcod.KEY_RELEASED)
                if key.vk == libtcod.KEY_ENTER:
                    if cursor_pos == 0:
                        menu_done = True
                        self.enter_game = True
                    elif cursor_pos == 1:
                        # TODO
                        pass
                    elif cursor_pos == 2:
                        menu_done = True
                        self.enter_game = False
                    else:
                        logging.error("Menu should not be here")


                if key.vk == libtcod.KEY_NONE:
                    break
                if time.time() - past_time > .2:
                    past_time = time.time()
                    if key.vk == libtcod.KEY_UP and cursor_pos > 0:
                        cursor_pos-=1
                    if key.vk == libtcod.KEY_DOWN and cursor_pos < len(menu)-1:
                        cursor_pos+=1

            if libtcod.console_is_window_closed():
                return
            libtcod.console_print(menu_con, 0, 0, "%c%c%c%cCave Dweller%c"%(libtcod.COLCTRL_FORE_RGB,255,1,1,libtcod.COLCTRL_STOP))
            for index, item in enumerate(menu):
                if cursor_pos == index:
                    the_format = (255,255,255)
                else:
                    the_format = (155, 155, 155)
                libtcod.console_print(menu_con, 0, index+1, "%c%c%c%c%s%c"%(libtcod.COLCTRL_FORE_RGB,the_format[0], the_format[1], the_format[2], item, libtcod.COLCTRL_STOP))
            libtcod.console_blit(menu_con, 0, 0, 0, 0, 0, Game.screen_width//2 - 10, Game.screen_height//2-2)
            libtcod.console_flush()
            time.sleep(Game.action_interval)
