"""
Pathfinding Module
------------------

This module contains a pathfinding algorithm for 2D labyrinths represented as numpy arrays.
It can be imported or run directly. When executed from the terminal, a labyrinth map file
can be provided (Python array syntax).

Labyrinth map conventions:
    0 : wall
    1 : empty cell
    2 : start cell
    3 : finish cell

The algorithm propagates distances from the start (+1) and finish (-1) simultaneously
until they meet, then reconstructs the shortest path.
"""
import numpy as np
import sys
import time

# -------------------------
# Global variables (for visualization/debugging)
# -------------------------
states = []  # List of propagation states for visualization
walls = None # Wall mask used for plotting

# -------------------------
# Constants
# -------------------------
INT_MAX = np.iinfo(np.int64).max
INT_MIN = np.iinfo(np.int64).min

# -------------------------
# Shift functions
# -------------------------
def shift_down(a: np.ndarray) -> np.ndarray:
    """Return a matrix shifted down by one row; top row is zeros."""
    out = np.zeros_like(a)
    out[1:] = a[:-1]
    return out

def shift_up(a: np.ndarray) -> np.ndarray:
    """Return a matrix shifted up by one row; bottom row is zeros."""
    out = np.zeros_like(a)
    out[:-1] = a[1:]
    return out

def shift_left(a: np.ndarray) -> np.ndarray:
    """Return a matrix shifted left by one column; rightmost column is zeros."""
    out = np.zeros_like(a)
    out[:, :-1] = a[:, 1:]
    return out

def shift_right(a: np.ndarray) -> np.ndarray:
    """Return a matrix shifted right by one column; leftmost column is zeros."""
    out = np.zeros_like(a)
    out[:, 1:] = a[:, :-1]
    return out

# -------------------------
# Labyrinth generation
# -------------------------
def generate_random_labyrinth(s: int, complexity: float = 0.4) -> np.ndarray:
    """
    Generate a random labyrinth of size s x s.

    Args:
        s (int): Size of labyrinth (rows = cols = s)
        complexity (float): Probability of a wall. Default 0.4

    Returns:
        np.ndarray: Labyrinth matrix with 0 = wall, 1 = empty, 2 = start, 3 = finish
    """
    lab_map = np.where(np.random.rand(s, s) < complexity, 0, 1)

    # Pick start and finish positions (must not be identical)
    a, b, c, d = [np.random.randint(0, s) for _ in range(4)]
    while a == c and b == d:
        a = np.random.randint(0, s)

    lab_map[a, b] = 2  # Start
    lab_map[c, d] = 3  # Finish

    return lab_map

# -------------------------
# Initialization
# -------------------------
def initialize(labyrinth_map: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    """
    Prepare the labyrinth for pathfinding.

    Args:
        labyrinth_map (np.ndarray): 2D map of labyrinth

    Returns:
        tuple:
            - wall_mask: 1 for empty cells, 0 for walls
            - initial_state: start = +1, finish = -1, others = 0
            - min_dist: Manhattan distance / 2 (lower bound for path steps)
    """
    start = np.argwhere(labyrinth_map == 2)
    finish = np.argwhere(labyrinth_map == 3)

    if len(start) != 1 or len(finish) != 1:
        print("Initialization error: There should be exactly one start (2) and one finish (3).")
        sys.exit()

    start = start[0]
    finish = finish[0]

    dist = (abs(start[0] - finish[0]) + abs(start[1] - finish[1]) - 1) / 2

    wall_mask = np.where(labyrinth_map == 0, 0, 1)
    initial_state = np.zeros_like(labyrinth_map)
    initial_state[start[0], start[1]] = 1
    initial_state[finish[0], finish[1]] = -1

    return wall_mask, initial_state, dist

# -------------------------
# Pathfinder
# -------------------------
def find_shortest_path(labyrinth_map: np.ndarray, visualize: bool = False):
    """
    Find the shortest path from start to finish.

    Args:
        labyrinth_map (np.ndarray): Labyrinth map
        visualize (bool): If True, store states for visualization

    Returns:
        tuple:
            - path (list of tuples) or None
            - propagation_time (ns)
            - reconstruction_time (ns)
            - steps (int)
    """
    global walls

    start_time = time.time_ns()

    wall_mask, state, min_dist = initialize(labyrinth_map)
    walls = wall_mask

    path_found = False
    step = 1
    meetpoints = None
    states.append(state.copy())

    prev_min_neg = 0
    prev_max_pos = 0

    while not path_found:
        up = shift_up(state)
        right = shift_right(state)

        # Check for collision (start/finish fronts meet)
        if step >= min_dist:
            collision = (up * state < 0) | (right * state < 0)
            if collision.any():
                path_found = True
                meetpoints = np.argwhere(collision)
                break

        # Propagate distances
        down = shift_down(state)
        left = shift_left(state)

        neighbors = np.stack([up, down, left, right])
        pos = np.where(neighbors > 0, neighbors, INT_MAX).min(axis=0)
        neg = np.where(neighbors < 0, neighbors, INT_MIN).max(axis=0)
        new_distances = np.where(pos != INT_MAX, pos + 1,
                                 np.where(neg != INT_MIN, neg - 1, 0))
        new_distances *= np.where(state == 0, wall_mask, 0)  # Only update empty cells

        state += new_distances
        step += 1

        if visualize:
            states.append(state.copy())

        max_pos = np.where(state > 0, state, INT_MIN).max()
        min_neg = np.where(state < 0, state, INT_MAX).min()

        # Check for no progress, meaning no solution
        if abs(max_pos + min_neg) > 1 or (min_neg == prev_min_neg and max_pos == prev_max_pos):
            return None, time.time_ns() - start_time, 0, step

        prev_max_pos = max_pos
        prev_min_neg = min_neg

    # -------------------------
    # Path reconstruction
    # -------------------------
    elapsed1 = time.time_ns() - start_time
    start_time = time.time_ns()
    path = []

    if path_found:
        s = state.shape
        x, y = int(meetpoints[0][0]), int(meetpoints[0][1])
        path.append((x, y))

        # From meetpoint to start
        while state[x, y] != 1:
            smallest = ((0, 0), np.inf)
            neighbors = []
            if x >= 1: neighbors.append((x-1, y))
            if y >= 1: neighbors.append((x, y-1))
            if x < s[0]-1: neighbors.append((x+1, y))
            if y < s[1]-1: neighbors.append((x, y+1))

            for i, j in neighbors:
                val = state[i, j]
                if val > 0 and val < smallest[1]:
                    smallest = ((i, j), val)

            x, y = smallest[0]
            path.append((x, y))
        path.reverse()

        # From meetpoint to finish
        x, y = int(meetpoints[0][0]), int(meetpoints[0][1])
        while state[x, y] != -1:
            largest = ((0, 0), -1000000000)
            neighbors = []
            if x >= 1: neighbors.append((x-1, y))
            if y >= 1: neighbors.append((x, y-1))
            if x < s[0]-1: neighbors.append((x+1, y))
            if y < s[1]-1: neighbors.append((x, y+1))

            for i, j in neighbors:
                val = state[i, j]
                if val < 0 and val > largest[1]:
                    largest = ((i, j), val)

            x, y = largest[0]
            path.append((x, y))

    elapsed2 = time.time_ns() - start_time
    return path, elapsed1, elapsed2, step


if __name__ == "__main__":
    """
    Visualization Script
    --------------------
    This section runs when the module is executed directly from the terminal.
    It generates a random labyrinth, computes the shortest path, and allows the 
    user to step through the propagation process using matplotlib.

    Controls:
        - Right arrow: advance one step
        - Left arrow: go back one step
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use("TkAgg")  # Use TkAgg backend for interactive plotting

    # Current frame index for stepping through states
    current = 0
    fig, ax = plt.subplots()

    def update_plot():
        """Update the matplotlib plot to display the current propagation state."""
        mat = states[current]

        # Plot walls + propagation matrix
        im = ax.imshow(
            mat + walls*.5,
            cmap="seismic",      # Red/blue for start/finish fronts
            interpolation="none" # No smoothing
        )

        # Optional: annotate cell values for debugging
        # for i in range(mat.shape[0]):
        #     for j in range(mat.shape[1]):
        #         ax.text(
        #             j, i,
        #             f"{mat[i, j]}",
        #             ha="center", va="center",
        #             color="black"
        #         )

        fig.canvas.draw()

    def on_press(event):
        """Handle left/right key presses to step through the propagation frames."""
        global current
        if event.key == 'right':
            current = (current + 1) % len(states)
            print(f"Step forward → frame {current}")  # Debug print
        elif event.key == 'left':
            current = (current - 1) % len(states)
            print(f"Step backward → frame {current}")  # Debug print

        update_plot()

    # -------------------------
    # Generate labyrinth and solve
    # -------------------------
    s = 50  # Labyrinth size
    lab_map = generate_random_labyrinth(s)
    #print("Generated labyrinth:")
    #print(lab_map)  # Debug: show the labyrinth in the terminal

    # Find shortest path and store all propagation states
    path, propagation_time, reconstruction_time, steps = find_shortest_path(lab_map, visualize=True)
    if path:
        print(f"Path found in {steps} steps!")
        print("Shortest path:", path)
        print(f"Propagation time: {propagation_time / 1e6:.2f} ms")
        print(f"Path reconstruction time: {reconstruction_time / 1e6:.2f} ms")
    else:
        print("No path exists for this labyrinth.")

    # -------------------------
    # Set up interactive plotting
    # -------------------------

    l = np.zeros((s, s))

    if path: 
        for i, j in path:
            l[i, j] = .5

    states.append(l)

    fig.canvas.mpl_connect('key_press_event', on_press)
    update_plot()
    plt.show()
