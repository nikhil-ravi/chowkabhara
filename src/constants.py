import numpy as np
import json

WIDTH = 700
HEIGHT = 700

ROWS = 7
COLS = 7
SQUARES = ROWS * COLS
SQSIZE = WIDTH // ROWS

LINE_WIDTH = 5

BG_COLOR = (24, 24, 24)
LINE_COLOR = (25, 65, 124)
CROSS_COLOR = (66, 66, 66)

PIECES_PER_PLAYER = 6

with open("src/piece_placements.json", "r") as f:
    IMG_CENTERS = json.load(f, object_hook=lambda x: {int(k): v for k, v in x.items()})

SAFE_HOUSES = [
    (0, 0),
    (0, 3),
    (0, 6),
    (1, 1),
    (1, 5),
    (3, 0),
    (3, 3),
    (3, 6),
    (5, 1),
    (5, 5),
    (6, 0),
    (6, 3),
    (6, 6),
]

BASE_GRID = np.array(
    [
        [15, 14, 13, 12, 11, 10, 9],
        [16, 28, 29, 30, 31, 32, 8],
        [17, 27, 42, 43, 44, 33, 7],
        [18, 26, 41, 48, 45, 34, 6],
        [19, 25, 40, 47, 46, 35, 5],
        [20, 24, 39, 38, 37, 36, 4],
        [21, 22, 23, 0, 1, 2, 3],
    ]
)

GRID_OFFSET = 100

PLACES_BEFORE_INNER = 23
PLACES_TO_FRUIT = 48
