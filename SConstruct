from subprocess import call
# build cave_dweller cython code
call(Split("./setup.py build_ext --inplace"))
# build mynoise C extension code
call(Split('./mynoise/setup.py build_ext --inplace'))
# build draw_text c/sdl code
SConscript("draw_text/SConstruct")
