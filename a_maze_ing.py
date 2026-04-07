import sys
from maze_generator import MazeGenerator


def parse_config(file_path: str) -> dict:
    config = {}

    try:
        with open(file_path, "r") as f:
            for line in f:

                line = line.strip()

                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    print("Invalid line:", line)
                    continue

                key, value = line.split("=")

                config[key.strip()] = value.strip()

        required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE"]

        for key in required:
            if key not in config:
                raise ValueError(f"Missing key: {key}")

        config["WIDTH"] = int(config["WIDTH"])
        config["HEIGHT"] = int(config["HEIGHT"])
        config["ENTRY"] = tuple(map(int, config["ENTRY"].split(",")))
        config["EXIT"] = tuple(map(int, config["EXIT"].split(",")))

    except Exception as e:
        print("Error reading config:", e)
        exit(1)

    return config


def display_maze(grid):

    height = len(grid)
    width = len(grid[0])

    for y in range(height):

        top = ""
        middle = ""

        for x in range(width):

            cell = grid[y][x]

            # top wall
            if cell & 1:
                top += "+---"
            else:
                top += "+   "

            # left wall
            if cell & 8:
                middle += "|"
            else:
                middle += " "

            # 🔥 STRONG VISIBILITY
            if cell == 15:
                middle += "███"   # VERY visible
            else:
                middle += "   "

        print(top + "+")
        print(middle + "|")

    print("+---" * width + "+")


def write_output(file_name, grid, entry, exit, path):

    try:
        with open(file_name, "w") as f:

            for row in grid:
                line = ""

                for cell in row:
                    line += hex(cell)[2:].upper()

                f.write(line + "\n")

            f.write("\n")

            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")
            f.write(path + "\n")

    except Exception as e:
        print("Error writing file:", e)


def main():

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return

    config = parse_config(sys.argv[1])

    maze = MazeGenerator(
        config["WIDTH"],
        config["HEIGHT"],
        int(config.get("SEED", 0))
    )

    maze.generate()

    # temporary path
    path = "TEST"

    display_maze(maze.grid)

    write_output(
        config["OUTPUT_FILE"],
        maze.grid,
        config["ENTRY"],
        config["EXIT"],
        path
    )


if __name__ == "__main__":
    main()
