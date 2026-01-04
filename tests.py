import solver
import numpy as np

def test_initialization():
    lab_map = np.array([
        [0, 2, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [1, 1, 1, 1, 0],
        [1, 1, 1, 0, 0],
        [1, 3, 1, 1, 0],
    ])

    print(solver.initialize(lab_map))

test_initialization()