"""Handles initialization of libtcod tile font, and the multiple sizes that a font can be"""
import os

from . import libtcodpy as libtcod

from . import game
from .util import game_path

# the behavior of this funtion changed after libtcod.init_root()
# Assess screen size statically
resolution = libtcod.sys_get_current_resolution()

class FontHandler(object):
    """
    Handles determining best font size for screen, setting current font, loading font
    via libtcod
    """

    def __init__(self, font_index=None):
        self.font_sizes = [16, 12, 10]
        self.font_size_index = None
        if font_index is None:
            self.font_size_index = self.determine_font_index()
        else:
            self.font_size_index = font_index
        self.set_font(self.font_size_index)

    def set_font(self, font_index=None):
        """Select font from font index"""
        # TODO modify libtcod to fix cursor problem with resize
        if font_index == None:
            font_index = self.font_size_index
        font_path = game_path(os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png')
            .format(size=self.font_sizes[self.font_size_index]))
        libtcod.console_set_custom_font(font_path,
            libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    def determine_font_index(self):
        """Set font size based on resolution"""
        for index, size in enumerate(self.font_sizes):
            res_x, res_y = resolution
            if not (game.Game.screen_height * size + 50 > res_y or
                    game.Game.screen_width * size > res_x):
                font_index = index
                break
        else:
            # Last font size will be the smallest
            font_index = len(self.font_sizes) - 1
        return font_index

    def decrease_font(self):
        """
        Decrease font size to the next available font.
        Stateful. does not return anything.
        """
        change_sucessful = None
        if self.font_size_index < len(self.font_sizes) - 1:
            self.font_size_index += 1
            change_sucessful = True
        else:
            change_sucessful = False
        return change_sucessful

    def increase_font(self):
        """
        Increase font size to the next size available font.
        Stateful. Does not return anything.
        """
        change_sucessful = None
        if self.font_size_index > 0:
            self.font_size_index -= 1
            change_sucessful = True
        else:
            change_sucessful = False
        return change_sucessful
