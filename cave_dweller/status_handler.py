import collections

import libtcodpy as libtcod

from game import Game

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
        self.ordered_status['debug'] = []

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
        for a_list in self.ordered_status.values():
            status_list.append(''.join(a_list))
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
