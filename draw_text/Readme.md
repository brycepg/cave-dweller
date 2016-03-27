This is a mini-module for making True-type fonts available in libtcod+python via the `sys_register_SDL_renderer` and SDL_ttf

It requires you to install SDL1.2, SDL_ttf, gcc

to compile for use with Python:

    sudo apt-get install gcc sdl1.2debian SDL-ttf2.0-dev
    make

then

    import draw_text
    ...
    tile_size=16
    font_size=16 # Default

    # draw text via the render callback
    def render(surface):
        # Draw onto surface at 25x25 in pixels from top-left
        draw_text.draw_text("it works!", surface, 25, 25)
    # Set the render function
    libtcod.sys_register_SDL_renderer(render)

If You acutally want to erase the text, then you need to call `console_set_dirty` 
after console_flush for the location at which you render the text

    ...
    def main_loop():
        While True:
            libtcod.console_flush()
            libtcod.console_set_dirty(x, y, w, h ) # In tile coordinates

If you want to set a custom font/size:

# Custom font + size
draw_text.set_font("foo.ttf", pt_size=12)

# Default font + different size
draw_text.set_font(None, pt_size=10)

Note that this is in pt instead of pixel since that's how ttfs are specified, 
and sdl_ttf doesn't allow for floating point values(i.e 11.5pt)
