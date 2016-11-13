LIBS=-lm
OPTS=--std=c++14 -Wall
SOURCES=simplex.c gen_map.cpp main.cpp
CC=g++
DEBUG_OPTS=-g
BUILD_OPTS=-O2
simplex: _PHONY
	$(CC) $(BUILD_OPTS) simplex.c $(LIBS) -shared -fPIC -o noise.so

build: _PHONY
	$(eval TYPE := $(shell echo $@ | tr '[:lower:'] '[:upper:]'))
	$(CC) $(OPTS) $($(TYPE)_OPTS) $(SOURCES) $(LIBS) $(ARGS)

debug: _PHONY
	$(eval TYPE := $(shell echo $@ | tr '[:lower:'] '[:upper:]'))
	$(CC) $(OPTS) $($(TYPE)_OPTS) $(SOURCES) $(LIBS) $(ARGS)

_PHONY:

