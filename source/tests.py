import solver
import numpy as np
import matplotlib.pyplot as plt

def test_initialization():
    lab_map = np.array([
        [0, 2, 1, 1, 0],
        [0, 1, 0, 1, 0],
        [1, 1, 1, 1, 0],
        [1, 1, 1, 0, 0],
        [1, 1, 3, 1, 0],
    ])

    print(solver.initialize(lab_map))

def test_speed(size=100, count=100):

    max_time = 0
    min_time = 1_000_000_000_000
    total_time = 0

    matrix_calculations = []
    path_building = []
    steps = []

    for i in range(count):

        lab_map = solver.generate_random_labyrinth(size)

        print(i+1)

        path, elapsed1, elapsed2, step = solver.find_shortest_path(lab_map)

        matrix_calculations.append(elapsed1 / 1_000_000)
        path_building.append(elapsed2 / 1_000_000)
        steps.append(step)

        elapsed = elapsed1 + elapsed2

        total_time += elapsed

        if elapsed > max_time:
            max_time = elapsed

        if elapsed < min_time:
            min_time = elapsed


    m = max(matrix_calculations)
    n = max(steps)
    plt.hist([matrix_calculations], bins=np.arange(0, m, m / 20), edgecolor='blue')
    plt.show()

    plt.hist([steps], bins=np.arange(0, n, n / 20), color ="red")
    plt.show()

    print(f"Max time: {max_time // 1_000_000}ms")
    print(f"Min time: {min_time // 1_000_000}ms")
    print(f"Total time: {total_time // 1_000_000}ms")

#test_initialization()
test_speed(10, 10000)