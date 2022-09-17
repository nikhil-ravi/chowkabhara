from typing import Tuple
import pygame

from constants import SQSIZE
from move import Move
from piece import Piece
from square import Square


class Dragger:
    """The Dragger class to handle the dragging of pieces."""

    def __init__(self):
        self.piece = None
        self.dragging = False
        self.mouseX = 0
        self.mouseY = 0
        self.initial_row = 0
        self.initial_col = 0

    # blit method

    def update_blit(self, surface: pygame.Surface):
        """Updates the surface to reflect the dragging of pieces.

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
        """
        # texture
        self.piece.set_texture(size=128)
        texture = self.piece.texture
        # img
        img = pygame.image.load(texture)
        # rect
        img_center = (self.mouseX, self.mouseY)
        self.piece.texture_rect = img.get_rect(center=img_center)
        # blit
        surface.blit(img, self.piece.texture_rect)

    # other methods

    def update_mouse(self, pos: Tuple[int, int]):
        """Update the mouse coordinates as the dragger moves.

        Args:
            pos (Tuple[int, int]): The row, col pair of the new mouse position.
        """
        self.mouseX, self.mouseY = pos  # (xcor, ycor)

    def save_initial(self, pos: Tuple[int, int]):
        """Save the initial piece position to bring it back in case it was dragged
        to an invalid location.

        Args:
            pos (Tuple[int, int]): The row, col pair of the initial piece position.
        """
        self.initial_row = pos[1] // SQSIZE
        self.initial_col = pos[0] // SQSIZE

    def drag_piece(self, piece: Piece):
        """Sets the dragging piece.

        Args:
            piece (Piece): The piece to set the dragging piece to.
        """
        self.piece = piece
        self.dragging = True

    def undrag_piece(self):
        """Resets the dragger."""
        self.piece = None
        self.dragging = False

    def get_move_from_initial_final(
        self, initial: Square, final: Square
    ) -> Move | None:
        """Given an initial square and a final square, check in the piece's moves list
        for a move with the given initial and final squares and return it if present,
        else return None.

        Args:
            initial (Square): The initial square.
            final (Square): The final square.

        Returns:
            Move | None:
             - Move: If a move with the initial and final squares is present, return it.
             - None: Else, return None.
        """
        for move in self.piece.moves:
            if move.initial == initial and move.final == final:
                return move
        return None
