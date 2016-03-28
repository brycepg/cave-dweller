ARGS=
draw_text_dir=draw_text
noise_dir=mynoise
drawmake=cd $(draw_text_dir) && make
noisemake=cd $(noise_dir) && make

build: build_draw build_noise

build_draw:
	$(drawmake)

build_noise:
	$(noisemake)

run:
	./cave-dweller.py

clean:
	rm -fr *.pyo *.pyc __pycache__ cave_dweller/*.pyc dist build *.svg
	$(noisemake) clean
	$(drawmake) clean

_PHONY:

exe: _PHONY
	# Does not work yet
	pyinstaller --onefile --windowed cave-dweller.py

UNITTEST=py.test
tests: _PHONY
	$(UNITTEST) --benchmark-disable tests $(ARGS)

bench: _PHONY
	$(UNITTEST) --benchmark-only tests $(ARGS)

testbench: _PHONY
	$(UNITTEST) tests $(ARGS)

coverage: _PHONY
	coverage run --source cave_dweller/ `which $(UNITTEST)` --benchmark-disable tests
	coverage html --omit cave_dweller/libtcodpy.py
