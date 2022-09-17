from typing import Tuple
from enum import Enum
from dataclasses import dataclass


@dataclass(eq=True)
class ThemeColors:
    """The dataclass for the theme's background color.

    Args:
        light (Tuple[int, int, int]): The light color to be used in a theme.
        dark (Tuple[int, int, int]): The dark color to be used in a theme.
    """

    light: Tuple[int, int, int]  # light color
    dark: Tuple[int, int, int]  # dark color


class Theme(Enum):
    """Enum of themes available to the user."""

    green = ThemeColors((234, 235, 200), (119, 154, 88))
    brown = ThemeColors((235, 209, 166), (165, 117, 88))
    blue = ThemeColors((229, 228, 200), (60, 95, 135))
    gray = ThemeColors((120, 119, 118), (86, 85, 84))
