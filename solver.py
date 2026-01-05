"""
This is the module containing the actual pathfinder. It can either be imported in another module \
or be launched directly from the terminal. In the latter case, a path to a file containing the \
labyrinth's map in python array syntax should be provided.
"""
import numpy as np
import sys
import time

## Utility functions
def shift_down(a):
    out = np.zeros_like(a)
    out[1:] = a[:-1]
    return out

def shift_up(a):
    out = np.zeros_like(a)
    out[:-1] = a[1:]
    return out

def shift_left(a):
    out = np.zeros_like(a)
    out[:, :-1] = a[:, 1:]
    return out

def shift_right(a):
    out = np.zeros_like(a)
    out[:, 1:] = a[:, :-1]
    return out


def initialize(labyrinth_map: np.ndarray) -> tuple:
    """\
This function's goal is to convert the map given to a structure useful for the algorithm.
This function expect the following properties about the provided matrix:
    - There should be exactly one cell marked as start (2) as well as exactly one marked as finish (3)

It works as follow:
    - use the original map to generate a mask (numpy matrix) where walls are encoded by 0s and \
any other cell is set to 1.
    - still using the original map, create a numpy matrix where the start is represented by +1 \
and the finish by -1, everything else is filled with 0s
"""
    # check that there is indeed only one start and one finish
    start = np.argwhere(labyrinth_map == 2)
    finish = np.argwhere(labyrinth_map == 3)

    if len(start) != 1 or len(finish) != 1:
        print("Initialization error: The map given doesn't follow the syntax, there should be only \
one start and one finish")
        sys.exit() # TODO: Handle this exception better

    # We get the actual coordinates
    start = start[0]
    finish = finish[0]

    # Calculate manathan distance between the end and the start then divide bytwo to get the expected minimum lenght of the path
    dist = abs(start[0] - finish[0]) + abs(start[1] - finish[1]) -1
    dist /= 2

    wall_mask = np.where(labyrinth_map == 0, 0, 1)
    initial_state = np.zeros_like(labyrinth_map) # create a matrix containing only infinities
    initial_state[start[0], start[1]] = 1
    initial_state[finish[0], finish[1]] = -1

    return (wall_mask, initial_state, dist)


def find_shortest_path(labyrinth_map: np.ndarray) -> list:
    """This function is the true entry point of the pathfinder. It takes in the the labyrinth's \
map and output the shortest path from the start to the end of the labyrinth"""
    wall_mask, state, min_dist = initialize(labyrinth_map)
    previous_state = np.copy(state)

    path_found = False
    step = 1

    meetpoints = None

    while not path_found:
        up = shift_up(state)
        right = shift_right(state)

        ### Check if we found a path ###
        if step >= min_dist:
            vertical_check = np.argwhere(up * state < 0)
            horizontal_check = np.argwhere(up * state < 0)

            if len(vertical_check) > 0 or len(horizontal_check) > 0:
                # That's it we have it
                #print("We have it !")
                #print(up * state)
                #print(right * state)
                path_found = True
                meetpoints = np.append(vertical_check, horizontal_check, axis=0)
                #print(meetpoints)
                break

        ### Propagate the distances in each direction ###
        down = shift_down(state)
        left = shift_left(state)

        new_distances = up

        for m in [right, down, left]:
            mask = m != 0

            np.copyto(new_distances, m, where=(new_distances < 0) & (new_distances < m) & mask)
            np.copyto(new_distances, m, where=(new_distances > 0) & (new_distances > m) & mask)
            np.copyto(new_distances, m, where=new_distances == 0)

        new_distances = np.where(new_distances < 0, new_distances-1, new_distances)
        new_distances = np.where(new_distances > 0, new_distances+1, new_distances)

        mask = np.where(state == 0, 1, 0)
        state += new_distances * mask * wall_mask

        
        #print(state)

        ### Check that we are not stuck
        if (state == previous_state).all():
            #print("No solution exist for this labyrinth")
            return None

        previous_state = state.copy()
        step += 1


    if path_found:
        # Reconsruct the path from the meeting point

        s = state.shape

        x, y = int(meetpoints[0][0]), int(meetpoints[0][1])
        path = [(x, y)]

        # first go from the meetpoint to the start
        while state[x, y] != 1:
            # look for the smallest positive number in th neibourhood
            smallest = ((0, 0), np.inf)

            neibourhood = []
            if x >= 1: neibourhood.append((x-1, y))
            if y >= 1: neibourhood.append((x, y-1))
            if x < s[0]-1: neibourhood.append((x+1, y))
            if y < s[1]-1: neibourhood.append((x, y+1))

            for i, j in neibourhood:
                val = state[i, j]
                #print(val, smallest, len(neibourhood))

                if val > 0 and val < smallest[1]:
                    smallest = ((i, j), val)
            
            x, y = smallest[0]
            path.append((x, y))

        path.reverse()

        x, y = int(meetpoints[0][0]), int(meetpoints[0][1])

        # now go from the meetpoint to the end
        while state[x, y] != -1:
            # look for the largest negative number in the neibourhood
            largest = ((0, 0), -100000)

            neibourhood = []
            if x >= 1: neibourhood.append((x-1, y))
            if y >= 1: neibourhood.append((x  , y-1))
            if x < s[0]-1: neibourhood.append((x+1, y))
            if y < s[1]-1: neibourhood.append((x  , y+1))

            for i, j in neibourhood:
                val = state[i, j]
                #print(val,largest)

                if val < 0 and val > largest[1]:
                    largest = ((i, j), val)
            
            x, y = largest[0]
            path.append((x, y))

        return path




if __name__ == "__main__":
    lab_map = np.array([
        [0, 2, 1, 0, 0],
        [0, 1, 0, 1, 0],
        [1, 1, 1, 1, 1],
        [1, 1, 1, 0, 1],
        [1, 1, 1, 3, 1],
    ])

    s = 100


    max_time = 0
    min_time = 1_000_000
    total_time = 0

    for i in range(1000):
        lab_map = np.where(np.random.rand(s, s) < .4, 0, 1)

        a, b, c, d = [np.random.randint(0, s), np.random.randint(0, s), np.random.randint(0, s), np.random.randint(0, s)]

        while a == c and b == d: a = np.random.randint(0, s)

        lab_map[a, b] = 2
        lab_map[c, d] = 3

        #print(lab_map)

        print(i+1)

        start_time = time.time_ns()
        path = find_shortest_path(lab_map)

        elapsed = time.time_ns() - start_time

        total_time += elapsed

        if elapsed > max_time:
            max_time = elapsed

        if elapsed < min_time:
            min_time = elapsed

    print(f"Max time: {max_time // 1_000_000}ms")
    print(f"Min time: {min_time // 1_000_000}ms")
    print(f"Total time: {total_time // 1_000_000}ms")
    #print(path)