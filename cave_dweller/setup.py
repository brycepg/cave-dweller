#!/usr/bin/python3 env

import sys
from cx_Freeze import setup, Executable

base = None
if sys.platform == "win32":
    base = "Win32GUI"

includes = ["noise"]
setup(name='Cave Dweller',
      version='0.0.5',
      description='Roguelike game -- Explore caves',
      options = {
          "build_exe" : {
              "includes": includes,
              },
          },
      executables=[Executable("cave_dweller.py", base=base)]
  )
