from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Optional

# Bits for CLOSED walls (1 means closed)
N = 1
E = 2
S = 4
W = 8

DIRS = [
    (0, -1, N, S),
    (1, 0, E, W),
    (0, 1, S, N),
    (-1, 0, W, E),
]


@dataclass(frozen=True)
class MazeParams:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    perfect: bool
    seed: Optional[int] = None


class MazeGenerator:
    """DFS-based maze generator producing grid cells in [0..15].

    grid[y][x] uses bits N,E,S,W where 1 means wall is CLOSED.
    """

    def __init__(self, params: MazeParams):
        self.params = params
        if params.seed is not None:
            random.seed(params.seed)

        self.grid: list[list[int]] = [[15 for _ in range(params.width)] for _ in range(params.height)]
        self.blocked: set[tuple[int, int]] = set()  # kept for compatibility (empty)

    def _in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.params.width and 0 <= y < self.params.height

    def _neighbors(self, x: int, y: int):
        for dx, dy, wall, opposite in DIRS:
            nx, ny = x + dx, y + dy
            if self._in_bounds(nx, ny):
                yield nx, ny, wall, opposite

    def _carve_between(self, x: int, y: int, nx: int, ny: int, wall: int, opposite: int) -> None:
        self.grid[y][x] &= ~wall
        self.grid[ny][nx] &= ~opposite

    def generate(self) -> None:
        """Generate perfect/imperfect maze. (No 42 pattern)."""
        self.blocked = set()
        self._dfs_from_entry()

        if not self.params.perfect:
            self._add_loops(loop_factor=0.08)

    def _dfs_from_entry(self) -> None:
        ex, ey = self.params.entry
        visited: set[tuple[int, int]] = set()

        def dfs(x: int, y: int) -> None:
            visited.add((x, y))
            neigh = list(self._neighbors(x, y))
            random.shuffle(neigh)

            for nx, ny, wall, opposite in neigh:
                if (nx, ny) in visited:
                    continue
                self._carve_between(x, y, nx, ny, wall, opposite)
                dfs(nx, ny)

        dfs(ex, ey)

    def _add_loops(self, loop_factor: float) -> None:
        """Add extra random openings to create cycles (imperfect)."""
        w, h = self.params.width, self.params.height
        attempts = max(1, int(w * h * loop_factor))

        for _ in range(attempts):
            x = random.randrange(w)
            y = random.randrange(h)
            neigh = list(self._neighbors(x, y))
            if not neigh:
                continue
            nx, ny, wall, opp = random.choice(neigh)
            self._carve_between(x, y, nx, ny, wall, opp)
