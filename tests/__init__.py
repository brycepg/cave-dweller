import sys
import os
cave_module = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cave_dweller")
print(cave_module)
sys.path.append(cave_module)
import test
