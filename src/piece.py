from __future__ import annotations
from enum import Enum
import os
from typing import List
from constants import PLACES_TO_FRUIT, PLACES_BEFORE_INNER

class Piece:
    
    def __init__(self, color: PieceColor, texture= None, texture_rect =None):
        self.color = color
        self.home_position = PieceColor[self.color].value * 100
        self.position = self.home_position * 1
        self.final_outer_position = self.home_position + PLACES_BEFORE_INNER
        self.fruit_position = self.home_position + PLACES_TO_FRUIT
        self.moves = []
        self.texture = texture
        self.texture_rect = texture_rect
        self.img_center = None
        self.set_texture()
    
    def move(self, places):
        if self.can_move(places):
            self.position += places
    
    def can_move(self, places):
        return (self.position + places) <= self.fruit_position
    
    def is_fruit(self):
        return self.position == self.fruit_position
    
    def add_move(self, move):
        self.moves.append(move)
    
    def clear_moves(self):
        self.moves = []
    
    def return_to_home(self):
        if not self.is_fruit():
            self.position = self.home_position * 1
    
    def set_texture(self, size:int=80):
        self.texture = os.path.join(f"assets/images/imgs-{size}px/{self.color}.png")

class TiedPiece(Piece):
    def __init__(self, color: PieceColor, pieces: List[Piece]):
        self.pieces = pieces
        self.position = self.pieces[0].position
        super().__init__(color)
    
    def can_move(self, places):
        return ((places % 2) == 0 and (self.position + places) <= self.fruit_position)
    
    def return_to_home(self):
        if not self.is_fruit():
            for piece in self.pieces:
                piece.return_to_home()
    
 
class PieceColor(Enum):
    """A class of colors for the players."""
    Red = 0
    Green = 1
    Blue = 2
    Yellow = 3
    