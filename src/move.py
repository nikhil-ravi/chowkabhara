from dataclasses import dataclass
from typing import Optional
from square import Square


@dataclass
class Move:
    """A dataclass to represent a move. It contains a initial Square and a final
    Square. A move that ties two piece together to create a TiedPiece needs a further
    tying_move field to be passed with a value set at True."""
    initial: Square
    final: Square
    tying_move: Optional[bool] = False
    
    def __repr__(self):
        return f"({self.initial.row}, {self.initial.col}) -> ({self.final.row}, {self.final.col})"

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final
