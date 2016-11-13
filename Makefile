build: _PHONY
	pyinstaller --onefile --windowed src/cave_dweller.py

run:
	./cave_dweller/cave_dweller.py

clean:
	rm -r *.pyo *.pyc __pycache__ cave_dweller/*.pyc dist build

_PHONY:
