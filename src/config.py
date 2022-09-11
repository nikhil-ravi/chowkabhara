import pygame
import os
from theme import Theme
from sound import Sound


class Config:
    def __init__(self):
        self.themes = list(Theme.__members__.keys())
        self.idx = 0
        self.theme = Theme[self.themes[self.idx]]
        self.font = pygame.font.SysFont("monospace", 18, bold=True)
        self.move_sound = Sound(os.path.join("assets/sounds/move.wav"))
        self.capture_sound = Sound(os.path.join("assets/sounds/capture.wav"))

    def change_theme(self):
        self.idx += 1
        self.idx %= len(self.themes)
        self.theme = Theme[self.themes[self.idx]]
