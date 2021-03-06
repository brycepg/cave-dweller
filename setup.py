#!/usr/bin/env python2 
from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os

ext_modules=[
        Extension("cave_dweller/gen_map",
        sources=["cave_dweller/gen_map.pyx"],
        libraries=["trng4"],
        language="c++",
        )]

setup(
  name = 'gen_map',
  ext_modules = cythonize(ext_modules),
)
