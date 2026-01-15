This project is a labyrinth pathfinder implementing a vectorization of the A algorithm. The implementation is made with Numpy for the computations and Matplotlib for the visualisation. It was created with focus on performance and scalability. Here is an overview of the project's structure:

- `source`: 
    The project source code in python:
        - `solver.py`: The entire code of the algorithm.
        - `tests.py`: A test suite used to mesure the performance of the algorithm at different scales.

- `graphs`:
    A collection of graphs showing the runtime performance of the algorithm at different scales (generated using the `test.py` module)

- `requirements.txt`:
    The complete list of requirements to run the project (Note that Matplotlib is not needed if you only intend to use the solver as a module and never call it directly)


## Using the program
Launching the `solver` modlue directly will show the steps of the solving of a 50x50 randomly generated layrinth. If you wish to call the code from your own script, import and use the `find_shortest_path` function. It takes one mendatory argument as well as two optional arguments:

- `labyrinth_map`: 
    As the name implies, it is a representation of the labyrinth in a numpy matrix. The walls are represented by 0s, the starting point, by 2, the end by 3 and every other cell is filled with a 1. Note that the function will return an error if the labyrinth doesn't have exactly *one* start and *one* end.

- `visualize`: 
    A boolean that decide whether the function should keep track of the steps of the search and how often. Set it to zero or less to disable that functionality.

- `states`:
    An array that the function will fill with the state of the search at each step. This argument is requiered if visualization is activated


## The algorithm

### Concept

The algorithm is based on the A* one.

The idea is to propagate signed distance from both the end and the start, and then detect the first square were the two "teams" meets. In other word, we check whether two cells of opposit signs sit next to each other. 

Unlike the classical A*, were each cell is treated individually and the state updated accordingly, thus needing a stack and a powerful heuristic to reduce the algorithmic complexity, our algorithm is much simpler. The use of matrix operations means that the distances can be progated in waves. This, by the same mean, ensure the validity of the path found as (one) most optimal path.

### Implementation

The first step of the algorithm, though not strictly part of it, is to turn the given map into a useful structure for the next steps.
The `generate_random_labyrinth` is well docummented in that regard. To sumarize, we have two matrices:

- a mask that keeps track of the positions of the walls, let's call it `W`
- an state matrix that is iniatialed with a 1 for the start and a -1 for the end. Every other cell is set to 0. Lets's call this one `S`

We now enter a loop that end if we either find a valid path or if we meet a dead end. At each step we:
- Compute the shifted version of the stated matrix in every direction (`Up`, `Left`, `Right`, `Down`);
- Check if a valid path is found by computing the products `S * Up` and `S * Right` and checking for negative values (meaning that the two wavefront met);
- Compute a new wave front for the positive numbers as well as the negative ones (For that we check the four shifted matrices for the non-null number with the smallest distance to zero);
- Combine the two waves fronts in a new matrix after incrementing the absolute values accordingly;
- Mask from the previous matrix the cells that were already present in `S`, we have a new mask M
- Update the state: `S += W * M`. The multiplication with the wall mask prevent us from going through the walls;
- Go to the next step of the loop

Here is a visualisation of what it would look like for a 3x3 map.
After initialization, we may have:
```
        |-1  0  0 |                       | 1  0  1 |
S =     | 0  0  0 |               W =     | 1  0  1 |
        | 0  0  1 |                       | 1  1  1 |

First iteration:
        
        | 0  0  0 |                       | 0  1  0 |
Up  =   | 0  0  1 |               Right = | 0  0  0 |
        | 0  0  0 |                       | 0  0  0 |
        
        | 0  0  0 |                       | 0  0  0 |
Left =  | 0  0  0 |               Down =  |-1  0  0 |
        | 0  1  0 |                       | 0  0  0 |

        | 0  0  0 |                       | 0  0  0 |
S * Up =| 0  0  0 |            S * Right =| 0  0  0 |
        | 0  0  0 |                       | 0  0  0 |

        No path found, keep going

        | 0 -2  0 |                       | 0  0  0 |
M =     |-2  0  2 |               W * M = |-2  0  2 |
        | 0  2  0 |                       | 0  2  0 |

        |-1  0  0 |                
S =     |-2  0  2 |          
        | 0  2  1 |           

Second iteration:

        |-2  0  2 |                       | 0 -1  0 |
Up =    | 0  2  1 |               Right = | 0 -2  0 |
        | 0  0  0 |                       | 0  0  2 |

        | 0  0  0 |                       | 0  0  0 |
Left =  | 0  2  0 |               Down =  |-1  0  0 |
        | 2  1  0 |                       |-2  0  2 |

        | 2  0  0 |                       | 0  0  0 |
S * Up =| 0  0  2 |            S * Right =| 0  0  0 |
        | 0  0  0 |                       | 0  0  2 |

        No path found, keep going
           

        | 0 -2  3 |                       | 0  0  3 |
M =     | 0  3  0 |               W * M = | 0  0  0 |
        |-3  0  0 |                       |-3  0  0 |

        |-1  0  3 |                
S =     |-2  0  2 |          
        |-3  2  1 |      

Third iteration:

        |-2  0  2 |                       | 0 -1  0 |
Up =    |-3  2  1 |               Right = | 0 -2  0 |
        | 0  0  0 |                       | 0 -3  2 |

        | 2  0  6 |                       | 0  0  0 |
S * Up =| 6  0  2 |            S * Right =| 0  0  0 |
        | 0  0  0 |                       | 0 -6  2 |

        Meetpoint found at (2, 1)
```     

Once a meeting point it found, constructing the whole path is a trival task.

###  Improvements

- We added a small heuristic to avoid checking for a valid path until it is physically possible for one to have been found.
- Another heuristic involving comparing the size of each wave front allow to check is the algorithm meet a dead end, avoiding wasting time on unsolvable cases.