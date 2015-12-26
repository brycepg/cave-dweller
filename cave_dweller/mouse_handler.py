import libtcodpy as libtcod

from game import Game

class Mouse:
    def __init__(self, mouse):
        self.mouse = mouse

        self.draw_x = None
        self.draw_y = None

        self.abs_x = None
        self.abs_y = None

    def update_coords(self):
        self.draw_x, self.draw_y = self.evaluate_mouse()
        if (self.draw_x and self.draw_y and
            self.mouse.cx < Game.game_width and
            self.mouse.cy < Game.game_height):
            self.abs_x = self.draw_x + Game.view_x
            self.abs_y = self.draw_y + Game.view_y
        else:
            self.abs_x = None
            self.abs_y = None

    def evaluate_mouse(self):
        """Returns mouse coordinates
           If the mouse is not active, return None"""
        # There's a bug where has mouse focus returns true if the mouse starts on
        # the console. (hence the edge checks to still place mouse if the
        # coordinates are not on the edge)
        if (libtcod.console_has_mouse_focus() or
            ((self.mouse.cx != 0 and self.mouse.cy != 0) and
             (self.mouse.cx != 0 and self.mouse.cy != Game.screen_height-1) and
             (self.mouse.cx != Game.screen_width-1 and self.mouse.cy != Game.screen_height-1) and
             (self.mouse.cx != Game.screen_width-1 and self.mouse.cy != 0))):
            x = self.mouse.cx
            y = self.mouse.cy
        else:
            x = None
            y = None

        return x, y


    def conditional_print(self):
        """Print mouse if within frame"""
        x, y = self.evaluate_mouse()
        if x and y:
            libtcod.console_put_char_ex(Game.mouse_con,
                                        x, y,
                                        ord('x'), libtcod.yellow, None)
