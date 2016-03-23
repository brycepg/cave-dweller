"""
Mini library to draw text to an sdl surface for SDL1.2

requires compilation of main.c via makefile(which requires sdl and sdl_ttf)

use draw_text(text) to draw text
When done call clean_up() to free C allocations

16px == 12pt
10px == 7.5pt (TTF_OpenFont requires an Int point size unfortunately)
12px == 9pt
8px == 6pt

"""
import os
from ctypes import *

cur_dir = os.path.dirname(__file__)
_lib = CDLL(os.path.join(cur_dir, "draw_text.so"))

_lib.init_ttf.argtypes = []
_lib.init_ttf.restype = c_int

_lib.set_font.argtypes = [c_char_p, c_int]
_lib.set_font.restype = c_int

_lib.draw_text.argtypes = [c_char_p, c_int, c_int, c_void_p, c_int, c_int, c_int]
_lib.draw_text.restype = c_int

_lib.clean_up.argtypes = []
_lib.clean_up.restype = c_int

default_font = os.path.join(os.path.join(cur_dir, os.path.join("ttf-bitstream-vera-1.10", "Vera.ttf")))
ttf_initialized = False

def init_ttf(font_path=default_font, use_font=True, pt_size=12):
    """
    Initalize the SDL TTF API

    set the .ttf file at font_path to render text in the draw_text function
    """
    global ttf_initialized
    if ttf_initialized:
        raise RuntimeError("sdl_ttf is already initialized")

    ret = _lib.init_ttf()
    if ret == -1:
        raise RuntimeError("sdl_ttf did not initialize properly")

    # By default set font
    if use_font:
        set_font(font_path, pt_size)

    ttf_initialized = True

def set_font(font_path=default_font, pt_size=12):
    """
    Set the ttf font at font_path and set its size to to be of size pt_size
    """
    if not ttf_initialized:
        init_ttf(use_font=False)
    font_ret = _lib.set_font(font_path, pt_size)
    if font_ret == -1:
        if not os.path.exists(font_path):
            msg = "{font_path} does not exist".format(font_path)
        else:
            msg = "{font_path} did not load correctly(needs to be a ttf?)".format(font_path)
        raise RuntimeError(msg)

def draw_text(text, surface_pointer, loc_x=0, loc_y=0, color=None):
    """
    render text  on the surface_pointer from the libtcod sys_register_surface callback
    Note: there is no type checking on surface_pointer, so be careful

    loc_x, loc_y is the location of the text in pixels

    color is a rgb tuple
        defaut: (155,155,155)

    raises RuntimeError if the text didn't render properly
    """
    if color is None:
        color = (155,155,155)
    if not ttf_initialized:
        init_ttf()
    ret = _lib.draw_text(text, loc_x, loc_y, surface_pointer, *color)
    if ret == -1:
        raise RuntimeError("The text did not render properly")

def cleanup_up():
    lib.clean_up()
