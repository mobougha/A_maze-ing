import random

# WALLS
N = 1
E = 2
S = 4
W = 8


class MazeGenerator:

    def __init__(self, width, height, seed=None):
        self.width = width
        self.height = height

        if seed is not None:
            random.seed(seed)

        self.grid = [[15 for _ in range(width)] for _ in range(height)]

        # pattern visibility
        self.pattern = [[False for _ in range(width)] for _ in range(height)]

    def generate(self):

        visited = set()

        def dfs(x, y):
            visited.add((x, y))

            directions = [
                (0, -1, N, S),
                (1, 0, E, W),
                (0, 1, S, N),
                (-1, 0, W, E),
            ]

            random.shuffle(directions)

            for dx, dy, wall, opposite in directions:

                nx = x + dx
                ny = y + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:

                    if (nx, ny) not in visited:

                        self.grid[y][x] &= ~wall
                        self.grid[ny][nx] &= ~opposite

                        dfs(nx, ny)

        dfs(0, 0)

        # add visible 42 pattern
        self.add_42_pattern()

    def add_42_pattern(self):

        # start position (center area)
        start_x = self.width // 4
        start_y = self.height // 4

        # -------- DRAW 4 --------
        for i in range(6):
            self.grid[start_y + i][start_x] = 15
            self.grid[start_y + i][start_x + 2] = 15

        for j in range(3):
            self.grid[start_y + 3][start_x + j] = 15

        # -------- DRAW 2 --------
        offset_x = start_x + 5

        for j in range(5):
            self.grid[start_y][offset_x + j] = 15
            self.grid[start_y + 3][offset_x + j] = 15
            self.grid[start_y + 6][offset_x + j] = 15

        self.grid[start_y + 1][offset_x + 4] = 15
        self.grid[start_y + 2][offset_x + 4] = 15
        self.grid[start_y + 4][offset_x] = 15
        self.grid[start_y + 5][offset_x] = 15
