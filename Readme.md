This is a Procedural Simulation Rougelike I'm currently working on.

Right now:  

- on the fly world generation/serialization
- basic entiity generation
    - basic stable entity ecosystem
- basic player actions(movement, wait, dig, build, kill)

To kill(for entitites): `k + ↑↓←→`

To dig(for diggable tiles): `d + ↑↓←→`

To build(for generic wall tile): `b + ↑↓←→`

4-way movement with arrow keys

# Install

* Install python 2.7
* Install libtcod (dll)
* Install noise (python package)

Make sure libtcod.so is the right architecture for your computer/OS. The current is Linux 64-bit. If not, grab and combile the right version from the bitbucket repo: (https://bitbucket.org/libtcod/libtcod/downloads)

Install python 2.7 and then install noise

    pip install noise

# To Run

from the root directory run

    python cave_dweller/cave_dweller.py
