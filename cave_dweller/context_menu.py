import libtcodpy as libtcod

from game import Game

class ContextMenu:
    def __init__(self, x=0, y=0, width=20, height=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.cur_line = 0
        self.con = libtcod.console_new(width, height)
        text = []

    def write(self, text):
        if self.cur_line < self.height:
            libtcod.console_print(self.con, 0, self.cur_line, text)
            self.cur_line += 1

    def draw(self):
        libtcod.console_blit(self.con, 0, 0, 0, 0, 0, self.x, self.y)

    def clear(self):
        self.cur_line = 0
        libtcod.console_clear(0)
        libtcod.console_clear(self.con)
