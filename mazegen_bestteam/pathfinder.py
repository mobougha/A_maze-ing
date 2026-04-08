"""
Pathfinder module using BFS to find the shortest path in a maze.
"""

from collections import deque
from typing import List, Tuple, Optional, Deque, Set

# Direction bit constants (same as in maze_generator)
N = 1
E = 2
S = 4
W = 8

# Direction vectors and opposite bits
DIRS = [
    (0, -1, N, 'N'),   # North
    (1, 0, E, 'E'),    # East
    (0, 1, S, 'S'),    # South
    (-1, 0, W, 'W'),   # West
]


def find_shortest_path(grid: List[List[int]],
                       start: Tuple[int, int],
                       end: Tuple[int, int]) -> Optional[str]:
    """
    Find the shortest path from start to end using BFS.

    Args:
        grid: 2D list of cells, each cell is a bitmask of walls (1=closed).
        start: (x, y) coordinates of entrance.
        end: (x, y) coordinates of exit.

    Returns:
        A string of directions (N/E/S/W) representing the path,
        or None if no path exists.
    """
    height = len(grid)
    width = len(grid[0])
    sx, sy = start
    ex, ey = end

    # BFS queue: (x, y, path_string)
    queue: Deque[Tuple[int, int, str]] = deque()
    queue.append((sx, sy, ""))
    visited: Set[Tuple[int, int]] = set()
    visited.add((sx, sy))

    while queue:
        x, y, path = queue.popleft()

        if (x, y) == (ex, ey):
            return path

        for dx, dy, wall_bit, direction in DIRS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height:
                # Can we go through this wall?
                # wall_bit is the bit in the CURRENT cell that must be 0 (open)
                if (grid[y][x] & wall_bit) == 0 and (nx, ny) not in visited:
                    visited.add((nx, ny))
                    queue.append((nx, ny, path + direction))

    return None  # No path found