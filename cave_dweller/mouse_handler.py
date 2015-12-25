import libtcodpy as libtcod

from game import Game

def evaluate_mouse(mouse):
    """Returns mouse coordinates
       If the mouse is not active, return None"""
    # There's a bug where has mouse focus returns true if the mouse starts on
    # the console. (hence the edge checks to still place mouse if the
    # coordinates are not on the edge)
    if (libtcod.console_has_mouse_focus() or
        ((mouse.cx != 0 and mouse.cy != 0) and
         (mouse.cx != 0 and mouse.cy != Game.screen_height-1) and
         (mouse.cx != Game.screen_width-1 and mouse.cy != Game.screen_height-1) and
         (mouse.cx != Game.screen_width-1 and mouse.cy != 0))):
        x = mouse.cx
        y = mouse.cy
    else:
        x = None
        y = None

    return x, y


def conditional_print(mouse):
    """Print mouse if within frame"""
    x, y = evaluate_mouse(mouse)
    if x and y:
        libtcod.console_put_char_ex(Game.mouse_con,
                                    x, y,
                                    ord('x'), libtcod.yellow, None)
