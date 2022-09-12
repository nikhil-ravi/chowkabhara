from dataclasses import field, dataclass
from typing import List, Optional
from piece import Piece
from constants import ROWS, COLS, SAFE_HOUSES


@dataclass
class Square:
    row: int
    col: int
    pieces: Optional[List[Piece]] = field(default_factory=list)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def is_safe_house(self):
        return (self.row, self.col) in SAFE_HOUSES

    def has_pieces(self):
        return len(self.pieces) > 0

    def isempty(self):
        return not self.has_pieces()

    def has_team_piece(self, color):
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color == color:
                    return True
        return False

    def has_single_team_piece(self, color):
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color == color and piece.name == "Piece":
                    return True
        return False

    def get_other_single_team_piece(self, piece):
        if self.has_pieces():
            for other_piece in self.pieces:
                if (
                    other_piece.color == piece.color
                    and other_piece.name == "Piece"
                    and other_piece != piece
                ):
                    return other_piece

    def has_enemy_piece(self, color):
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color != color:
                    return True
        return False

    def get_enemy_pieces(self, color):
        return [piece for piece in self.pieces if piece.color != color]

    def isempty_or_enemy(self, color):
        return self.isempty() or self.has_enemy_piece(color)

    def add_piece(self, piece):
        self.pieces.append(piece)

    def remove_piece(self, piece):
        self.pieces.remove(piece)

    @staticmethod
    def in_range(*args):
        for arg in args:
            if arg < 0 or arg >= ROWS:
                raise SquareOutOfRangeException(arg)
        return True

    @staticmethod
    def get_alphacol(col):
        ALPHACOLS = {col_: chr(col_ + 97) for col_ in range(COLS)}
        return ALPHACOLS[col]


class SquareOutOfRangeException(Exception):
    def __init__(self, val, *args):
        super().__init__(args)
        self.val = val

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self):
        return f"The {self.val} is not in a valid range {0, ROWS-1}"
