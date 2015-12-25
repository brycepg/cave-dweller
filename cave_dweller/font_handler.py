import os 

import libtcodpy as libtcod

import game 

class FontHandler(object):

    def __init__(self):
        self.font_sizes = [16, 12, 10]
        self.font_size_index = None
        self.auto_set()

    def auto_set(self):
        self.font_size_index = self.determine_font_index()
        self.set_font(self.font_size_index)

    def set_font(self, font_index=None):
        """Select font from font index"""
        if font_index == None:
            font_index = self.font_size_index
        font_path = os.path.join('fonts', 'dejavu{size}x{size}_gs_tc.png'
                .format(size=self.font_sizes[self.font_size_index]))
        libtcod.console_set_custom_font(font_path,
            libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)

    def determine_font_index(self):
        """Set font size based on resolution"""
        for index, size in enumerate(self.font_sizes):
            res_x, res_y = libtcod.sys_get_current_resolution()
            if not (game.Game.screen_height * size + 100 > res_y or
                    game.Game.screen_width * size > res_x):
                font_index = index
                break
        else:
            # Last font size will be the smallest
            font_index = len(self.font_sizes) - 1
        return font_index

    def decrease_font(self):
        change_sucessful = None
        if self.font_size_index < len(self.font_sizes) - 1:
            self.font_size_index += 1
            change_sucessful = True
        else:
            change_sucessful = False
        return change_sucessful

    def increase_font(self):
        change_sucessful = None
        if self.font_size_index > 0:
            self.font_size_index -= 1
            change_sucessful = True
        else:
            change_sucessful = False
        return change_sucessful
