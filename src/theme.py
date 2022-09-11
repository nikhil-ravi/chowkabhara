from enum import Enum
from color import BG_Color


class Theme(Enum):
    green = BG_Color(
            (234, 235, 200),
            (119, 154, 88)
        )
    brown = BG_Color(
        (235, 209, 166),
        (165, 117, 88)
    )
    blue = BG_Color(
        (229, 228, 200),
        (60, 95, 135)
    )
    gray = BG_Color(
        (120, 119, 118),
        (86, 85, 84)
    )