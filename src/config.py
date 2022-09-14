import pygame
import os
from theme import Theme
from sound import Sound


class Config:
    """The rendering configuration for the game. Handles the theme, font, and sounds."""
    def __init__(self):
        self.themes = list(Theme.__members__.keys())
        self.idx = 0
        self.theme = Theme[self.themes[self.idx]]
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.move_sound = Sound(os.path.join("assets/sounds/move.wav"))
        self.capture_sound = Sound(os.path.join("assets/sounds/capture.wav"))

    def change_theme(self):
        """Change the theme to the next theme in the :py:class:`src.theme.Theme` Enum."""
        self.idx += 1
        self.idx %= len(self.themes)
        self.theme = Theme[self.themes[self.idx]]
