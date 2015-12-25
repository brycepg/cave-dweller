import libtcodpy as libtcod

white = libtcod.white
yellow = libtcod.yellow

def colorize(txt, lib_color):
    """Using libtcod color codes color txt"""
    # Values can't be zero?
    r = max(1, lib_color.r)
    g = max(1, lib_color.g)
    b = max(1, lib_color.b)
    colored_txt = "%c%c%c%c%s%c" % (libtcod.COLCTRL_FORE_RGB,
                                    r, g, b, txt,
                                    libtcod.COLCTRL_STOP)
    return colored_txt
