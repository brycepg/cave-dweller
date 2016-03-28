CC = gcc
SO_FLAGS = -fPIC -shared
INCLUDES = /usr/include/SDL
LIB = -Llibs -lSDL -lSDL_ttf
LIB_OUT = draw_text.so
STANDALONE_OUT = a.out
SOURCE = main.c

so: draw_text.so main.c
	$(CC) -o $(LIB_OUT) $(SOURCE) -I$(INCLUDES) $(SO_FLAGS) $(LIB)

standalone: main.c a.out
	$(CC) -o $(STANDALONE_OUT) $(SOURCE) -I$(INCLUDES) $(LIB) 

all: draw_text.so standalone lib

clean:
	rm -f *.pyc
