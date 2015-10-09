build: _PHONY
	pyinstaller --onefile --windowed src/cave_dweller.py

run:
	./src/cave_dweller.py

clean:
	rm -r *.pyo *.pyc __pycache__

_PHONY:
