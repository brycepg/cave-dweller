import libtcodpy as libtcod

# Player
lightest_gray = libtcod.lightest_gray 

white = libtcod.white # Cave Grass
black = libtcod.black # Spider

# Ground fg / wall bg / cat
gray = libtcod.gray

# Ground bg
darkest_gray = libtcod.darkest_gray

purple = libtcod.purple # Fungus
sepia = libtcod.sepia # mole

# Dead
red = libtcod.red

# Status Bar
darkest_yellow = libtcod.darkest_yellow
darkest_red = libtcod.darkest_red # Death too
darkest_sepia = libtcod.darkest_sepia

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
