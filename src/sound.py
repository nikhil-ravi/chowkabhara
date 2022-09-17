import pygame


class Sound:
    """The sound object to handle to sounds played on piece moves and captures.

    Args:
        path (str): The path to the sound file.
    """

    def __init__(self, path: str):
        self.path = path
        self.sound = pygame.mixer.Sound(self.path)

    def play(self):
        """Play the sound."""
        pygame.mixer.Sound.play(self.sound)
