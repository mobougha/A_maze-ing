*This project has been created as part of the 42 curriculum by [mobougha] & [].*

# A-Maze-ing

## Description
A-Maze-ing is a Python-based maze generation and visualization tool. The primary goal of this project is to create complex, solvable mazes based on user-defined configurations, featuring a mandatory "42" pattern embedded into the center of the grid. The application provides a command-line interface and a terminal-based visualizer to explore the generated mazes.

## Instructions

### Prerequisites
- Python 3.8 or higher.
- A terminal with ANSI color support (standard on Linux/macOS).

### Execution
Run the application using the provided `Makefile` or directly with Python by passing a configuration file:
```bash
make run
# OR
python3 a_maze_ing.py config.txt
```

### Visualizer Controls
Once the visualizer is open:
- `P`: Toggle the solution path visibility.
- `R`: Regenerate the maze (follows the seed if provided).
- `C`: Cycle through different UI color schemes.
- `Q`: Quit the application.

## Config File Structure
The configuration file (`config.txt`) must follow a strict `KEY=VALUE` format. Blank lines and lines starting with `#` are ignored.

| Key | Description | Example |
| :--- | :--- | :--- |
| `WIDTH` | Number of columns (min 12 for pattern) | `20` |
| `HEIGHT` | Number of rows (min 12 for pattern) | `20` |
| `ENTRY` | Starting coordinates (x,y) | `0,0` |
| `EXIT` | Exit coordinates (x,y) | `19,19` |
| `OUTPUT_FILE` | Filename to save the hex grid | `maze.txt` |
| `PERFECT` | `true` for no loops, `false` for cycles | `false` |
| `SEED` | (Optional) String or integer for same results | `my_seed_123` |

## Technical Choices

### Maze Generation Algorithm
I chose the **Iterative Depth-First Search (DFS)** algorithm.

### Why this algorithm?
- **Solvability:** It guarantees every cell is reachable and there is exactly one path between any two points (before adding loops).
- **Aesthetics:** DFS creates long, winding corridors that are more challenging and visually interesting than algorithms like Prim's.
- **Robustness:** I implemented it **iteratively** using a manual stack instead of recursion. This prevents "Stack Overflow" errors when generating very large mazes (e.g., 500x500).

### Reusability
- **`MazeGenerator` Class:** This logic is entirely decoupled from the display. It can be imported into any other Python project to generate grids or solve paths without needing the terminal UI.
- **Hex Encoding logic:** the `save_maze` function adheres to the standard 4-bit wall encoding format, making the output compatible with other 42 maze projects.

## Resources
- [Wikipedia: Maze Generation Algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Python Random Module Documentation](https://docs.python.org/3/library/random.html)
- [ANSI Escape Codes for Terminal Styling](https://en.wikipedia.org/wiki/ANSI_escape_code)

### AI Usage
AI (Antigravity) was used as a pair-programmer for this project:
- **Algorithm Implementation:** Assisted in converting the recursive DFS logic into an iterative stack-based approach.
- **UI Design:** Helped design the `MazeRenderer` using ANSI escape codes for the "blocks" look and color schemes.
- **Debugging:** Assisted in troubleshooting seed reproducibility issues and configuration parsing edge cases.

## Project Management

### Roles
- **[LOGIN]:** Lead Developer - Responsible for core Generation logic, UI Rendering, and Project Architecture.

### Planning & Evolution
- **Initial Plan:** Build a simple DFS generator that outputs text.
- **Mid-Project:** Realized the need for an iterative approach to support larger grids and added the BFS solver to verify validity.
- **Final Phase:** Integrated the visualizer and the mandatory "42" pattern logic.

### Assessment
- **What worked well:** The iterative DFS approach proved very stable. The separation between `MazeGenerator` and `MazeRenderer` allowed for quick UI tweaks without breaking the generation.
- **Improvements:** Could add more algorithms (like Kruskal’s or Wilson’s) to offer different "styles" of mazes.
- **Tools used:** VS Code, Git, Python `unittest` for validation, and Antigravity AI.
