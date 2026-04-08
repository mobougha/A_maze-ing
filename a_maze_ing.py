from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

from maze_generator import MazeGenerator, MazeParams, N, W


@dataclass(frozen=True)
class Config:
    """Parsed and validated configuration for maze generation."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _parse_bool(value: str) -> bool:
    """Parse a string as a boolean.

    Accepts: true/false, 1/0, yes/no, y/n (case-insensitive).
    Raises ValueError on unrecognised values.
    """
    v = value.strip().lower()
    if v in {"true", "1", "yes", "y"}:
        return True
    if v in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r} (expected True/False)")


def _parse_xy(value: str) -> tuple[int, int]:
    """Parse 'x,y' into a pair of ints.

    Raises ValueError on bad format.
    """
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate {value!r} (expected 'x,y')")
    try:
        x = int(parts[0])
        y = int(parts[1])
    except ValueError as exc:
        raise ValueError(
            f"Invalid coordinate {value!r} (x,y must be integers)"
        ) from exc
    return (x, y)


def parse_config(file_path: str) -> Config:
    """Parse a KEY=VALUE config file and return a validated Config.

    Rules:
    - Blank lines and lines starting with '#' are ignored.
    - Each non-blank, non-comment line must be KEY=VALUE.
    - Duplicate keys are rejected.
    - Required keys: WIDTH, HEIGHT, ENTRY, EXIT, OUTPUT_FILE, PERFECT.
    - Optional key: SEED.

    Raises ValueError on invalid syntax/values, OSError on file errors.
    """
    raw: dict[str, str] = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue

            if "=" not in s:
                raise ValueError(
                    f"{file_path}:{lineno}: invalid line (missing '='): {s!r}"
                )

            key, value = s.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError(
                    f"{file_path}:{lineno}: empty key in line: {s!r}"
                )
            if key in raw:
                raise ValueError(
                    f"{file_path}:{lineno}: duplicate key: {key}"
                )

            raw[key] = value

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    for k in required:
        if k not in raw:
            raise ValueError(f"Missing required key: {k}")

    try:
        width = int(raw["WIDTH"])
    except ValueError as exc:
        raise ValueError(f"WIDTH must be an integer, got {raw['WIDTH']!r}") from exc

    try:
        height = int(raw["HEIGHT"])
    except ValueError as exc:
        raise ValueError(
            f"HEIGHT must be an integer, got {raw['HEIGHT']!r}"
        ) from exc

    entry = _parse_xy(raw["ENTRY"])
    exit_ = _parse_xy(raw["EXIT"])
    output_file = raw["OUTPUT_FILE"]
    perfect = _parse_bool(raw["PERFECT"])

    seed: Optional[int] = None
    if "SEED" in raw and raw["SEED"] != "":
        try:
            seed = int(raw["SEED"])
        except ValueError as exc:
            raise ValueError(
                f"SEED must be an integer, got {raw['SEED']!r}"
            ) from exc

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive integers (> 0)")

    ex, ey = entry
    xx, xy = exit_
    if not (0 <= ex < width and 0 <= ey < height):
        raise ValueError(
            f"ENTRY {entry} is out of bounds for a {width}×{height} maze"
        )
    if not (0 <= xx < width and 0 <= xy < height):
        raise ValueError(
            f"EXIT {exit_} is out of bounds for a {width}×{height} maze"
        )
    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different cells")

    if not output_file:
        raise ValueError("OUTPUT_FILE must not be empty")

    return Config(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=output_file,
        perfect=perfect,
        seed=seed,
    )


def display_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    show_path: bool = False,
    path: str = "",
) -> None:
    """Print an ASCII rendering of the maze to stdout.

    - Entry cell is marked 'E', exit cell is marked 'X'.
    - Cells with value 15 (all walls closed / part of '42' pattern) are
      rendered as solid block characters '███'.
    - If *show_path* is True, the path string is printed after the maze.
    """
    height = len(grid)
    width = len(grid[0])

    for y in range(height):
        top = ""
        middle = ""

        for x in range(width):
            cell = grid[y][x]

            # North wall
            top += "+---" if (cell & N) else "+   "

            # West wall
            middle += "|" if (cell & W) else " "

            if (x, y) == entry:
                middle += " E "
            elif (x, y) == exit_:
                middle += " X "
            elif cell == 15:
                middle += "███"
            else:
                middle += "   "

        print(top + "+")
        print(middle + "|")

    print("+---" * width + "+")

    if show_path:
        print(f"PATH({len(path)}): {path}")


def write_output(
    file_name: str,
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_: tuple[int, int],
    path: str,
) -> None:
    """Write the maze to *file_name* in the subject format.

    Format:
      - One hex-digit per cell, one row per line (uppercase, no separator).
      - Blank line separator.
      - Entry coordinates as 'x,y'.
      - Exit coordinates as 'x,y'.
      - Shortest path as N/E/S/W letters (empty string if unavailable).
    All lines end with a newline character.
    """
    with open(file_name, "w", encoding="utf-8") as f:
        for row in grid:
            f.write("".join(format(cell, "X") for cell in row) + "\n")
        f.write("\n")
        f.write(f"{entry[0]},{entry[1]}\n")
        f.write(f"{exit_[0]},{exit_[1]}\n")
        f.write(path + "\n")


def main() -> None:
    """Entry point: python3 a_maze_ing.py config.txt"""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        sys.exit(1)

    try:
        cfg = parse_config(sys.argv[1])
    except OSError as e:
        print(f"Error reading config file: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error in config: {e}")
        sys.exit(1)

    maze = MazeGenerator(
        MazeParams(
            width=cfg.width,
            height=cfg.height,
            entry=cfg.entry,
            exit=cfg.exit,
            perfect=cfg.perfect,
            seed=cfg.seed,
        )
    )

    maze.generate()

    try:
        path = maze.shortest_path()
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    display_maze(maze.grid, cfg.entry, cfg.exit, show_path=True, path=path)

    try:
        write_output(cfg.output_file, maze.grid, cfg.entry, cfg.exit, path)
    except OSError as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)

    print(f"Wrote maze to: {cfg.output_file}")


if __name__ == "__main__":
    main()
