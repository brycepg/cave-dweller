#include <unistd.h>
#include <stdbool.h>

#include "SDL/SDL.h"
#include "SDL_ttf.h"

SDL_Surface* text_surface = NULL;
TTF_Font *font = NULL; 


int init_ttf(void) 
{
    if( TTF_Init() == -1 ) 
    { 
        return -1;
    }
}

int set_font(char* font_path, int font_size) 
{
    if(font != NULL)
    {
        TTF_CloseFont(font);
    }
    font = TTF_OpenFont(font_path, font_size);
    if( font == NULL ) 
    { 
        return -1; 
    }
    return 0;
}


int draw_text(char* text, int loc_x, int loc_y, void* dst, int r, int g, int b)
{
    //The font that's going to be used 
    SDL_Color textColor = {r, g, b};
    SDL_Rect offset;
    offset.x = loc_x;
    offset.y = loc_y;

    text_surface = TTF_RenderText_Solid( font, text, textColor ); 
    if(text_surface == NULL)
    { 
        return -1; 
    }
    SDL_BlitSurface(text_surface, NULL, dst, &offset); //Update the screen 
    SDL_FreeSurface(text_surface);
    return 0;
}

int clean_up() 
{
    TTF_CloseFont(font);
    TTF_Quit();
    SDL_Quit();
    return 0;
}

int main( int argc, char* args[] ) {
    SDL_Surface* screen = NULL;
    SDL_WM_SetCaption( "TTF Test", NULL );
    if ( SDL_Init( SDL_INIT_EVERYTHING ) == -1 ) {
        return false;
    } 
    screen = SDL_SetVideoMode(640, 480, 32, SDL_SWSURFACE);
    init_ttf();
    set_font("ttf-bitstream-vera-1.10/Vera.ttf", 16);
    //If there was an error in rendering the text 
    ////Apply the images to the screen 
    draw_text("foo", 25, 25, screen, 155, 155, 155);
    if( SDL_Flip( screen ) == -1 ) { return 1; }
    sleep(1000);
    clean_up();
    return 0;
}

