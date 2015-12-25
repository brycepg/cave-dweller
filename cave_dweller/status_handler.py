import collections

import libtcodpy as libtcod

from game import Game
import actions
from colorizer import colorize

class StatusBar(object):
    def __init__(self):
        # Portion of window that's not the game
        self.status_bar_width = Game.screen_width
        self.status_bar_height = Game.screen_height - Game.game_height
        self.con = libtcod.console_new(self.status_bar_width,
                                        self.status_bar_height)
        self.ordered_status = collections.OrderedDict()
        self.ordered_status['turn'] = []
        self.ordered_status['kills'] = []
        self.ordered_status['mode'] = []
        self.ordered_status['debug'] = []

        self.is_mode_set = False

    def get_txt(self, player, world):
        """Generate status bar text for game"""
        # Dynamic status list
        self.ordered_status['turn'] = ['Turn ', str(world.turn)]
        if player.kills > 0:
            self.ordered_status['kills'] = [' Kills ', str(player.kills)]
        if Game.debug:
            self.ordered_status['debug'] = [' ', 'Debug']
        else:
            self.ordered_status['debug'] = []

        status_list = []
        for key in self.ordered_status:
            txt = ''.join(self.ordered_status[key])
            if key == 'mode':
                txt = colorize(txt, (255,255,1))
            status_list.append(txt)
        status_txt = ''.join(status_list)
        return status_txt


    def run(self, player, world):
        """Process information and print"""
        status_txt = self.get_txt(player, world)
        self.print_status(status_txt)

    def draw(self):
        """Blit status console"""
        # Draw to the right of the game window
        libtcod.console_blit(self.con, x=0, y=0, w=0, h=0,
                             dst=0, xdst=0, ydst=Game.game_height)

    def print_status(self, txt):
        """Print text to console"""
        libtcod.console_print(self.con, 0, 0, txt)

    def mode_set(self, key):
        """Detect which action is being performed and display to status"""
        for a_action in actions.PlayerAction.current_actions:
            if isinstance(a_action, actions.PlayerMoveAction):
                if key.pressed and key.c == a_action.state_key:
                    mode = type(a_action).__name__
                    self.ordered_status['mode'] = []
                    self.ordered_status['mode'].append(' ')
                    self.ordered_status['mode'].append(mode)
                    self.is_mode_set = True
                    #log.info("set %s",mode)
                if not key.pressed:
                    if len(self.ordered_status['mode']) > 1:
                        mode = self.ordered_status['mode'][1]
                        if mode and mode == type(a_action).__name__:
                            self.ordered_status['mode'] = []
