"""
This is the module containing the actual pathfinder. It can either be imported in another module \
or be launched directly from the terminal. In the latter case, a path to a file containing the \
labyrinth's map in python array syntax should be provided.
"""
import numpy as np
import sys
import time

def initialize(labyrinth_map: np.ndarray) -> tuple:
    """\
This function's goal is to convert the map given to a structure useful for the algorithm.
This function expect the following properties about the provided matrix:
    - There should be exactly one cell marked as start (2) as well as exactly one marked as finish (3)

It works as follow:
    - use the original map to generate a mask (numpy matrix) where walls are encoded by 0s and \
any other cell is set to 1.
    - still using the original map, create a numpy matrix where the start is represented by +1 \
and the finish by -1, everything else is filled with 'np.inf'
"""
    # check that there is indeed only one start and one finish
    start = np.argwhere(labyrinth_map == 2)
    finish = np.argwhere(labyrinth_map == 3)

    if len(start) != 1 or len(finish) != 1:
        print("Initialization error: The map given doesn't follow the syntax, there should be only \
one start and one finish")
        sys.exit() # TODO: Handle this exception better
    else:
        start = start[0]
        finish = finish[0] 

    wall_mask = np.where(labyrinth_map == 0, 0, 1)
    initial_state = np.where(labyrinth_map == 0, np.inf, np.inf) # create a matrix containing only infinities
    initial_state[start[0], start[1]] = 1
    initial_state[finish[0], finish[1]] = -1

    return (wall_mask, initial_state)

def find_shortest_path(labyrinth_map: np.ndarray) -> list:
    """This function is the true entry point of the pathfinder. It takes in the the labyrinth's \
map and output the shortest path from the start to the end of the labyrinth"""
    wall_mask, state = initialize(labyrinth_map)


if __name__ == "__main__":
    lab_map = np.array([
        [0, 2, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 0, 3],
        [1, 1, 1, 1, 1],
    ])

    start_time = time.time_ns()
    path = find_shortest_path(lab_map)
    print(f"Time elapsed: {(time.time_ns() - start_time) // 1_000_000}ms")
    print(path)