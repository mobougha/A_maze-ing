from __future__ import annotations

import random
import sys
from collections import deque
from dataclasses import dataclass
from typing import Optional

# Wall-bit encoding: 1 = closed, 0 = open
# bit0 North, bit1 East, bit2 South, bit3 West
N = 1
E = 2
S = 4
W = 8

# (dx, dy, wall_in_current_cell, opposite_wall_in_neighbor, direction_letter)
DIRS = [
    (0, -1, N, S, "N"),
    (1,  0, E, W, "E"),
    (0,  1, S, N, "S"),
    (-1, 0, W, E, "W"),
]


@dataclass(frozen=True)
class MazeParams:
    """Immutable parameters for maze generation."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool
    seed: Optional[int] = None


class MazeGenerator:
    """Generate a maze as a grid of wall bitmasks (each cell 0..15).

    Encoding: bit0=North(1), bit1=East(2), bit2=South(4), bit3=West(8).
    A set bit means the wall is closed; cleared bit means open passage.
    """

    def __init__(self, params: MazeParams) -> None:
        self.params = params
        self._rng = random.Random(params.seed)

        w, h = params.width, params.height
        self.grid: list[list[int]] = [[15] * w for _ in range(h)]
        # Cells that belong to the "42" pattern (fully closed, impassable)
        self.blocked: set[tuple[int, int]] = set()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is within the maze bounds."""
        return 0 <= x < self.params.width and 0 <= y < self.params.height

    def _neighbors(self, x: int, y: int):
        """Yield (nx, ny, wall, opposite, letter) for each in-bounds neighbor."""
        for dx, dy, wall, opposite, letter in DIRS:
            nx, ny = x + dx, y + dy
            if self._in_bounds(nx, ny):
                yield nx, ny, wall, opposite, letter

    def _carve_between(
        self, x: int, y: int, nx: int, ny: int, wall: int, opposite: int
    ) -> None:
        """Open the wall between (x,y) and (nx,ny)."""
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opposite

    # ------------------------------------------------------------------
    # Generation
    # ------------------------------------------------------------------

    def generate(self) -> None:
        """Generate the maze, then stamp the 42 pattern.

        The blocked cells are reserved *before* running DFS so the spanning
        tree is built only on passable cells.  This guarantees a path between
        any two non-blocked cells without needing retries.
        """
        entry = self.params.entry
        exit_ = self.params.exit
        w, h = self.params.width, self.params.height

        # Reset grid
        self.grid = [[15] * w for _ in range(h)]
        self.blocked = set()

        # Pre-compute the 42 pattern cells so we can reserve them during DFS
        cells = self._build_42_cells()
        if cells is None:
            print(
                "Warning: Maze too small to draw '42' pattern (need ≥12×9); "
                "skipping pattern."
            )
        else:
            # Fatal if entry/exit fall inside the pattern
            if entry in cells:
                print(
                    f"Error: ENTRY {entry} falls inside the '42' pattern. "
                    "Choose a different entry point."
                )
                sys.exit(1)
            if exit_ in cells:
                print(
                    f"Error: EXIT {exit_} falls inside the '42' pattern. "
                    "Choose a different exit point."
                )
                sys.exit(1)

            # Reserve blocked cells so DFS routes around them
            self.blocked = cells

        # Build spanning tree on non-blocked cells only
        self._dfs_generate(entry[0], entry[1])

        if not self.params.perfect:
            self._add_loops(loop_factor=0.08)

        # Stamp the 42 pattern (all walls closed)
        for x, y in self.blocked:
            self.grid[y][x] = 15

    def _dfs_generate(self, start_x: int, start_y: int) -> None:
        """Iterative DFS (recursive backtracker) spanning tree from (start_x, start_y).

        Blocked cells are skipped so the spanning tree only connects passable cells.
        """
        # Pre-seed visited with blocked cells so DFS never enters them
        visited: set[tuple[int, int]] = set(self.blocked)
        stack: list[tuple[int, int]] = [(start_x, start_y)]
        visited.add((start_x, start_y))

        while stack:
            x, y = stack[-1]
            unvisited = [
                (nx, ny, wall, opp)
                for nx, ny, wall, opp, _ in self._neighbors(x, y)
                if (nx, ny) not in visited
            ]

            if not unvisited:
                stack.pop()
                continue

            self._rng.shuffle(unvisited)
            nx, ny, wall, opposite = unvisited[0]
            self._carve_between(x, y, nx, ny, wall, opposite)
            visited.add((nx, ny))
            stack.append((nx, ny))

    def _add_loops(self, loop_factor: float) -> None:
        """Add extra openings to turn a perfect maze into an imperfect one."""
        w, h = self.params.width, self.params.height
        attempts = max(1, int(w * h * loop_factor))
        for _ in range(attempts):
            x = self._rng.randrange(w)
            y = self._rng.randrange(h)
            nbrs = list(self._neighbors(x, y))
            if nbrs:
                nx, ny, wall, opposite, _ = self._rng.choice(nbrs)
                self._carve_between(x, y, nx, ny, wall, opposite)

    # ------------------------------------------------------------------
    # "42" pattern
    # ------------------------------------------------------------------

    def _build_42_cells(self) -> Optional[set[tuple[int, int]]]:
        """Compute the set of cells that form the "42" pattern.

        Returns None if the maze is too small to fit the pattern.
        The pattern is centred in the grid.  It fits in a 10-wide × 7-tall box.
        Minimum grid size required: 12 wide, 9 tall.
        """
        min_w, min_h = 12, 9
        if self.params.width < min_w or self.params.height < min_h:
            return None

        start_x = (self.params.width - 10) // 2
        start_y = (self.params.height - 7) // 2

        cells: set[tuple[int, int]] = set()

        # "4": two vertical bars from row 0..6, horizontal bar at row 3
        for i in range(7):
            cells.add((start_x + 0, start_y + i))
            cells.add((start_x + 2, start_y + i))
        for j in range(3):
            cells.add((start_x + j, start_y + 3))

        # "2": horizontal bars at rows 0, 3, 6; verticals on right (rows 1-2)
        #      and left (rows 4-5)
        ox = start_x + 5
        for j in range(5):
            cells.add((ox + j, start_y + 0))
            cells.add((ox + j, start_y + 3))
            cells.add((ox + j, start_y + 6))
        cells.add((ox + 4, start_y + 1))
        cells.add((ox + 4, start_y + 2))
        cells.add((ox + 0, start_y + 4))
        cells.add((ox + 0, start_y + 5))

        return cells

    def _try_add_42_pattern(
        self,
        entry: tuple[int, int],
        exit_: tuple[int, int],
    ) -> bool:
        """Place the "42" pattern on the grid.

        Returns True on success (including "too small – skipped").
        Returns False if entry or exit would fall inside the pattern (caller
        should treat this as a fatal error).

        .. note::
            Under normal usage ``generate()`` handles pattern reservation
            *before* DFS.  This method is kept as a standalone utility for
            direct / external callers.
        """
        cells = self._build_42_cells()

        if cells is None:
            print(
                "Warning: Maze too small to draw '42' pattern (need ≥12×9); "
                "skipping pattern."
            )
            return True

        # Bounds check (should always pass given _build_42_cells logic, but
        # guard anyway)
        for x, y in cells:
            if not self._in_bounds(x, y):
                print(
                    "Warning: Internal error placing '42' pattern; "
                    "skipping pattern."
                )
                return True

        # Check entry/exit collision (fatal – config must be corrected)
        if entry in cells:
            print(
                f"Error: ENTRY {entry} falls inside the '42' pattern. "
                "Choose a different entry point."
            )
            return False
        if exit_ in cells:
            print(
                f"Error: EXIT {exit_} falls inside the '42' pattern. "
                "Choose a different exit point."
            )
            return False

        # Stamp the pattern
        for x, y in cells:
            self.grid[y][x] = 15
        self.blocked |= cells
        return True

    # Kept for backwards compatibility / direct use
    def add_42_pattern(self) -> None:
        """Public alias that applies the 42 pattern using current params."""
        self._try_add_42_pattern(self.params.entry, self.params.exit)

    # ------------------------------------------------------------------
    # Pathfinding
    # ------------------------------------------------------------------

    def shortest_path(self) -> str:
        """Return the shortest path from ENTRY to EXIT as a string of N/E/S/W.

        Raises ValueError if no path exists (e.g. the 42 pattern severed it).
        """
        start = self.params.entry
        goal = self.params.exit

        if start in self.blocked:
            raise ValueError("ENTRY is inside the blocked '42' pattern.")
        if goal in self.blocked:
            raise ValueError("EXIT is inside the blocked '42' pattern.")

        q: deque[tuple[int, int]] = deque([start])
        prev: dict[tuple[int, int], tuple[tuple[int, int], str]] = {}
        visited: set[tuple[int, int]] = {start}

        while q:
            x, y = q.popleft()
            if (x, y) == goal:
                break

            cell = self.grid[y][x]
            for dx, dy, wall, _opp, letter in DIRS:
                nx, ny = x + dx, y + dy
                if not self._in_bounds(nx, ny):
                    continue
                if (nx, ny) in self.blocked:
                    continue
                if cell & wall:
                    continue  # wall is closed

                nxt = (nx, ny)
                if nxt in visited:
                    continue

                visited.add(nxt)
                prev[nxt] = ((x, y), letter)
                q.append(nxt)

        if goal not in visited:
            raise ValueError("No valid path from ENTRY to EXIT.")

        steps: list[str] = []
        cur = goal
        while cur != start:
            p, letter = prev[cur]
            steps.append(letter)
            cur = p
        steps.reverse()
        return "".join(steps)
