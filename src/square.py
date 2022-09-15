from dataclasses import field, dataclass
from typing import List, Optional
from piece import Piece, PieceColor, TiedPiece
from constants import COLS, SAFE_HOUSES


@dataclass
class Square:
    """The square class to represent the squares on the board.

    Args:
        row (int): The row number of the square.
        col (int): The column number of the square.
        pieces (List[Piece | TiedPiece], optional): The pieces present in the square.
    """

    row: int
    col: int
    pieces: Optional[List[Piece]] = field(default_factory=list)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    @property
    def is_safe_house(self) -> bool:
        """Check if the square is a safe house.

        Returns:
            bool: True if the square is a safe house.
        """
        return (self.row, self.col) in SAFE_HOUSES

    def has_pieces(self) -> bool:
        """Check if the square has pieces.

        Returns:
            bool: True if the square has pieces.
        """
        return len(self.pieces) > 0

    def isempty(self) -> bool:
        """Check if the square is empty.

        Returns:
            bool: True if the square is empty.
        """
        return not self.has_pieces()

    def has_team_piece(self, color: PieceColor) -> bool:
        """Check if the square has a piece of the given color.

        Returns:
            bool: True if the square has a piece of the given color.
        """
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color == color:
                    return True
        return False

    def has_single_team_piece(self, color: PieceColor) -> bool:
        """Check if the square has a single (as in not a TiedPiece, not one) piece
        of the given color.

        Returns:
            bool: True if the square has a single (as in not a TiedPiece, not one)
            piece of the given color.
        """
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color == color and piece.name == "Piece":
                    return True
        return False

    def get_other_single_team_piece(self, piece: Piece) -> bool | None:
        """If the square has a single (as in not a TiedPiece, not one) piece
        of the same color as the given piece, then return it.

        Returns:
            bool | None: Return the piece on the square of the same color as the given piece.
            If none present, return None.
        """
        if self.has_pieces():
            for other_piece in self.pieces:
                if other_piece.color == piece.color and other_piece.name == "Piece" and other_piece != piece:
                    return other_piece
        return None

    def has_enemy_piece(self, color: PieceColor) -> bool:
        """Check whether a square has an enemy piece.

        Args:
            color (PieceColor): The player's color.

        Returns:
            bool: True if the square has an enemy piece.
        """
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color != color:
                    return True
        return False

    def has_enemy_tied_piece(self, color: PieceColor) -> bool:
        """Check whether the square has a TiedPiece belonging to an enemy player.

        Args:
            color (PieceColor): The player's color.

        Returns:
            bool: True if the square has an enemy TiedPiece.
        """
        if self.has_pieces():
            for piece in self.pieces:
                if piece.color != color and piece.name == "TiedPiece":
                    return True
        return False

    def get_enemy_pieces(self, color: PieceColor) -> List[Piece | TiedPiece]:
        """Return the enemy pieces.
        Returns:
            List[Piece | TiedPiece]: The list of enemy pieces.
        """
        return [piece for piece in self.pieces if piece.color != color]

    def isempty_or_enemy(self, color: PieceColor) -> bool:
        """Check if the square is either empty or has enemy pieces.

        Returns:
            bool: True if the square is either empty or has enemy pieces.
        """
        return self.isempty() or self.has_enemy_piece(color)

    def add_piece(self, piece: Piece | TiedPiece):
        """Add a piece to the square's pieces list."""
        self.pieces.append(piece)

    def remove_piece(self, piece: Piece | TiedPiece):
        """Remove a piece from the square's pieces list."""
        self.pieces.remove(piece)

    @staticmethod
    def get_alphacol(col: int) -> str:
        """Return the column's alphabetic character

        Args:
            col (int): The column number.

        Returns:
            str: The column's alphabetic character.
        """
        ALPHACOLS = {col_: chr(col_ + 97) for col_ in range(COLS)}
        return ALPHACOLS[col]


class InvalidAliasException(Exception):
    """Exception raised when an invalid alias is used."""

    def __init__(self, val, *args):
        super().__init__(args)
        self.val = val

    def __repr__(self) -> str:
        return super().__repr__()

    def __str__(self):
        return f"The {self.val} is not a valid alias."
