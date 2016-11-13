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

# Install

To run the game, you'll need to install:

* python 2.7
* noise (python package for simplex noise)
* SDL 1.2 for libtcod on linux?

Windows and linux dll/so s are included

After python 2.7 is installed, install noise via pip

    pip install noise

At some point i'll do releases with pyinstaller

# To Run

from the root directory run

    ./cave-dweller.py

# Gameplay

#### Digging(and viewable/hidden areas)

![Hidden Areas](media/hidden-areas.gif)

#### Fungus Growth in Fast Mode

![Fungus Growth](media/fungus-growth.gif)

#### An "Overworld"

!["Overworld"](media/4096.png)
