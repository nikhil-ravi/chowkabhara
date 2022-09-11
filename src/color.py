from dataclasses import dataclass


@dataclass(eq=True)
class BG_Color:
    light: tuple[int, int, int]
    dark: tuple[int, int, int]