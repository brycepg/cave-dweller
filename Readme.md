This is a Procedural Simulation Rougelike I'm currently working on.

# Current Features

- seed-based terrain generation
- on the fly world generation/serialization
- basic entiity generation
    - basic stable entity ecosystem
- turn-based movement
- basic player actions(movement, wait, dig, build, kill)

 # Controls

 * To kill(for entities): `k + ↑↓←→`
 * To dig(for diggable tiles): `d + ↑↓←→`
 * To build(for generic wall tile): `b + ↑↓←→`
 * '.' to wait, 
 * shift + '.' to fast wait, ESC to exit

Inspect with mouse
4-way movement with arrow keys
Shift . to enter fast mode

# Install

To run the game, you'll need to install:

* python 2.7
* noise (python package for simplex noise)
* SDL 1.2? Not for Windows?

Windows and linux dll/so s are included

After python 2.7 is installed, install noise via pip

    pip install noise

At some point i'll do releases with py2exe

# To Run

from the root directory run

    ./cave-dweller.py

# Image

![Fungus Growth](https://raw.githubusercontent.com/brycepg/cave-dweller/master/media/fungus-growth.gif)
