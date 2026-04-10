*This project has been created as part of the 42 curriculum by <login1> and <login2>.*

# A-Maze-ing

A-Maze-ing is a modular maze generator and solver written in Python. It produces a terminal maze that integrates the mandatory "42" pattern, computes the shortest solution path, and exports results to a standardized hexadecimal file.

## Algorithm

**Generation — Iterative Recursive Backtracker (DFS)**  
We chose the iterative DFS algorithm because it guarantees that every cell is reachable (a perfect spanning tree), is simple to implement, and produces aesthetically long corridors. Without interrupting the generation, we mark cells for the "42" pattern and then physically seal them (set all 4 walls to closed = 0xF) *after* the DFS runs, also correcting the neighboring cells' facing walls to maintain full wall coherence.

**Solving — BFS (Breadth-First Search)**  
BFS guarantees the absolute shortest path in an unweighted grid graph. The solution is returned as a direction string (N/E/S/W) and also saved to the output file.

## Features

- **"42" Pattern**: Mandatory visible pattern formed by fully-closed cells. Positioned at the center of the grid (requires >= 12×12). Entry/Exit cannot overlap the pattern. Warns if maze is too small.
- **Shortest Path**: BFS finds the optimal path, toggleable with `[P]`.
- **Interactive Terminal UI**: `[R]` Regen · `[P]` Path · `[C]` Color · `[Q]` Quit · `Ctrl+C` Exit
- **Exportable**: Saves maze grid (hex), entry/exit, and solution path to a file.

## Reusable Library (`mazegen`)

The `mazegen` package is a standalone importable module. It can be installed via pip:

```bash
pip install mazegen-bestteam-0.1.0-py3-none-any.whl
```

Then used in any Python project:

```python
from mazegen import MazeGenerator, MazeParams

params = MazeParams(width=20, height=20, entry=(0, 0), exit=(19, 19), perfect=True)
gen = MazeGenerator(params)
gen.generate()

print(gen.grid)          # 2D list[list[int]], hex cell bitmasks
print(gen.pattern_cells) # list of (x,y) of "42" pattern cells
print(gen.warning)       # Non-empty string if maze too small for "42"

path = gen.solve()       # 'NESSWN...' or None
```

### MazeParams attributes

| Parameter | Type | Description |
|-----------|------|-------------|
| `width` | `int` | Number of columns |
| `height` | `int` | Number of rows |
| `entry` | `tuple[int, int]` | Start cell (x, y) |
| `exit` | `tuple[int, int]` | Exit cell (x, y) |
| `perfect` | `bool` | `True` = no loops (spanning tree) |
| `seed` | `Optional[int]` | Random seed (None = system random) |

## Requirements

- Python 3.10+

## Installation

```bash
git clone <repository-url>
cd A_maze-ing
pip install -e .
```

Or install directly from the wheel:

```bash
pip install mazegen-bestteam-0.1.0-py3-none-any.whl
```

## Usage

```bash
python a_maze_ing.py config.txt
```

### Configuration Format

```ini
WIDTH=20            # Width of the maze
HEIGHT=20           # Height of the maze
ENTRY=0,0           # Start coordinates (x,y)
EXIT=19,19          # End coordinates (x,y)
OUTPUT_FILE=maze.txt
PERFECT=true        # true = no loops, false = imperfect
SEED=42             # Optional: integer seed for reproducibility
```

### Output File Format (`maze.txt`)

```
F9F5...   <- hexadecimal row (one char per cell)
...
           <- blank line separator
0,0        <- entry coordinates
19,19      <- exit coordinates
NNEESS...  <- shortest path directions (N/E/S/W)
```

## Makefile

```bash
make install       # Install dependencies
make run           # Run the program
make lint          # flake8 PEP8 check
make lint-strict   # mypy --strict type check
make build         # Build distributable package
make clean         # Remove build artifacts
```

> **Note**: On Windows, `make` is not installed by default. Use `python a_maze_ing.py config.txt` directly, or install `make` via Chocolatey: `choco install make`.

## Resources

- Python `random` module — for DFS shuffle
- Maze generation theory: [Wikipedia – Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- BFS shortest path: [Wikipedia – Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)
- AI assistance (Google Gemini / Antigravity) was used during this project to assist with code review, error correction, modularization, and documentation writing.

## Team

| Member | Role |
|--------|------|
| Developer A | Maze generation logic, DFS, pattern integration |
| Developer B | BFS solver, renderer, config parsing, packaging |

**Planning**: The project was split into two phases — (1) core generation + pattern, (2) solving + UI + packaging. Code reviews were done via pull requests. The main challenge was ensuring wall coherence when sealing "42" cells after DFS generation.
