from __future__ import annotations
from enum import Enum
import os
from typing import List, Optional
from constants import PLACES_TO_FRUIT, PLACES_BEFORE_INNER, GRID_OFFSET
import pygame

from move import Move

class Piece:
    """The piece class represents the piece on the board.
    
    Args:
        color (PieceColor): The color of the piece.
        texture (str): The path to the texture for the piece.
        texture_rect (pygame.Rect, optional): The rect of the texture for the piece.
    """
    def __init__(self, color: PieceColor, texture: Optional[str] = None, texture_rect: Optional[pygame.Rect] =None):
        self.color = color
        self.texture = texture
        self.texture_rect = texture_rect
        self.set_texture()
        
        self.name = "Piece"
        self.home_position = PieceColor[self.color].value * GRID_OFFSET
        self.position = self.home_position * 1
        self.final_outer_position = self.home_position + PLACES_BEFORE_INNER
        self.fruit_position = self.home_position + PLACES_TO_FRUIT
        self.moves = []
        self.img_center = None
        self.with_enemy_tied_piece = False
    
    def move(self, places: int):
        """Update the piece's position by the given number of places.

        Args:
            places (int): The number of places by which to increase the piece's 
            position by.
        """
        if self.can_move(places):
            self.position += places
    
    def can_move(self, places: int) -> bool:
        """Check if the piece can be moved by the given number of places.

        Args:
            places (int): The number of places by which to increase the piece's position.

        Returns:
            bool: Whether the piece can be moved by the given number of places.
        """
        return (self.position + places) <= self.fruit_position
    
    def is_fruit(self) -> bool:
        """Check whether the piece is already at the fruiting position.

        Returns:
            bool: Whether the piece is at the fruiting position.
        """
        return self.position == self.fruit_position
    
    def add_move(self, move: Move):
        """Adds a move to the pieces moves list.

        Args:
            move (Move): The move to add to the pieces moves list.
        """
        self.moves.append(move)
    
    def clear_moves(self):
        """Clears the pieces moves list."""
        self.moves = []
    
    def set_with_enemy_tied_piece(self):
        """Sets the with enemy TiedPiece Flag."""
        self.with_enemy_tied_piece = True
            
    def clear_with_enemy_tied_piece(self):
        """Clears the with enemy TiedPiece Flag."""
        self.with_enemy_tied_piece = False
            
    def return_to_home(self):
        """If the piece is not at the fruiting position, return it to its home
        position.
        """
        if not self.is_fruit():
            self.position = self.home_position * 1
    
    def set_texture(self, size:int=80):
        """Set the path to the texture of the given size.

        Args:
            size (int, optional): The size of the texture to be used. Defaults to 80.
        """
        self.texture = os.path.join(f"assets/images/imgs-{size}px/{self.color}.png")

class TiedPiece(Piece):
    def __init__(self, color: PieceColor, position: int, pieces: List[Piece]):
        super().__init__(color)
        self.pieces = pieces
        self.position = position
        self.name = "TiedPiece"
    
    def return_to_home(self):
        """If the piece is not at the fruiting position, return both its pieces
        to their home position.
        """
        if not self.is_fruit():
            for piece in self.pieces:
                piece.return_to_home()
    
    def set_texture(self, size:int=80):
        self.texture = os.path.join(f"assets/images/imgs-{size}px/Tied{self.color}.png")
        
    def __repr__(self) -> str:
        return f"{self.name}({self.color=}: {self.position=} with {self.pieces=})"
 
class PieceColor(Enum):
    """A class of colors for the players."""
    Red = 0
    Green = 1
    Blue = 2
    Yellow = 3
    