import libtcodpy as libtcod

def colorize(txt, rgb):
    """Using libtcod color codes color txt with rgb tuple"""
    colored_txt = "%c%c%c%c%s%c" % (libtcod.COLCTRL_FORE_RGB,
                                    rgb[0], rgb[1], rgb[2],
                                    txt,
                                    libtcod.COLCTRL_STOP)
    return colored_txt
