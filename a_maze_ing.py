from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import Optional

from mazegen_bestteam.maze_generator import MazeGenerator, MazeParams
from mazegen_bestteam.pathfinder import find_shortest_path
from renderer import MazeRenderer


@dataclass(frozen=True)
class Config:
    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None


def _parse_bool(value: str) -> bool:
    v = value.strip().lower()
    if v in {"true", "1", "yes", "y"}:
        return True
    if v in {"false", "0", "no", "n"}:
        return False
    raise ValueError(f"Invalid boolean value: {value!r} (expected True/False)")


def _parse_xy(value: str) -> tuple[int, int]:
    parts = [p.strip() for p in value.split(",")]
    if len(parts) != 2:
        raise ValueError(f"Invalid coordinate {value!r} (expected 'x,y')")
    return (int(parts[0]), int(parts[1]))


def parse_config(file_path: str) -> Config:
    raw: dict[str, str] = {}

    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if "=" not in s:
                raise ValueError(f"{file_path}:{lineno}: invalid line (missing '='): {s!r}")

            key, value = s.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                raise ValueError(f"{file_path}:{lineno}: empty key")
            if key in raw:
                raise ValueError(f"{file_path}:{lineno}: duplicate key: {key}")

            raw[key] = value

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    for k in required:
        if k not in raw:
            raise ValueError(f"Missing key: {k}")

    width = int(raw["WIDTH"])
    height = int(raw["HEIGHT"])
    entry = _parse_xy(raw["ENTRY"])
    exit_ = _parse_xy(raw["EXIT"])
    output_file = raw["OUTPUT_FILE"]
    perfect = _parse_bool(raw["PERFECT"])

    seed: Optional[int] = None
    if "SEED" in raw and raw["SEED"] != "":
        seed = int(raw["SEED"])

    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be > 0")
    if entry == exit_:
        raise ValueError("ENTRY and EXIT must be different")

    ex, ey = entry
    xx, xy = exit_
    if not (0 <= ex < width and 0 <= ey < height):
        raise ValueError(f"ENTRY out of bounds: {entry} for {width}x{height}")
    if not (0 <= xx < width and 0 <= xy < height):
        raise ValueError(f"EXIT out of bounds: {exit_} for {width}x{height}")

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





def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    try:
        cfg = parse_config(sys.argv[1])
        gen = MazeGenerator(
            MazeParams(
                width=cfg.width,
                height=cfg.height,
                entry=cfg.entry,
                exit=cfg.exit,
                perfect=cfg.perfect,
                seed=cfg.seed,
            )
        )
        gen.generate()
    except (OSError, ValueError) as e:
        print(f"Error: {e}")
        return

    path_str = find_shortest_path(gen.grid, cfg.entry, cfg.exit)
    if path_str is None:
        print("Warning: No path found from entry to exit!")

    renderer = MazeRenderer(gen.grid, cfg.entry, cfg.exit, gen.pattern_cells)
    renderer.set_path(path_str)

    while True:
        renderer.display()
        key = renderer.wait_key()
        if key == 'R':
            gen = MazeGenerator(
                MazeParams(
                    width=cfg.width,
                    height=cfg.height,
                    entry=cfg.entry,
                    exit=cfg.exit,
                    perfect=cfg.perfect,
                    seed=None,
                )
            )
            gen.generate()
            path_str = find_shortest_path(gen.grid, cfg.entry, cfg.exit) or ""
            renderer = MazeRenderer(gen.grid, cfg.entry, cfg.exit, gen.pattern_cells)
            renderer.set_path(path_str)
        elif key == 'P':
            renderer.toggle_path()
        elif key == 'C':
            renderer.cycle_color()
        elif key == 'Q':
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
