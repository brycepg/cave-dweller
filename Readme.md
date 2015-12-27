This is a Procedural Simulation Rougelike I'm currently working on.

# Current Features

- seed-based terrain generation
- on the fly world generation/serialization
- basic entiity generation
    - basic stable entity ecosystem
- basic player actions(movement, wait, dig, build, kill)

 # Controls

 * To kill(for entities): `k + ↑↓←→`
 * To dig(for diggable tiles): `d + ↑↓←→`
 * To build(for generic wall tile): `b + ↑↓←→`
 * '.' to wait

Inspect with mouse
4-way movement with arrow keys
Shift . to enter fast mode

# Install

To run the game, you'll need to install:

* python 2.7
* libtcod (dll)
* SDL 1.2 (for libtcod)
* noise (python package for simplex noise)

Make sure libtcod.so is the right architecture for your computer/OS. The current is Linux 64-bit. If not, grab and combile the right version from the bitbucket repo: (https://bitbucket.org/libtcod/libtcod/downloads)

After python 2.7 is installed, install noise via pip

    pip install noise

At some point i'll do releases with py2exe

# To Run

from the root directory run

    ./cave-dweller.py

# Image

(https://raw.githubusercontent.com/brycepg/cave-dweller/master/media/fungus-growth.gif)
