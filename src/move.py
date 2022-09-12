from square import Square


class Move:
    def __init__(self, initial: Square, final: Square, tying_move: bool = False):
        self.initial = initial
        self.final = final
        self.tying_move = tying_move

    def __str__(self):
        return f"({self.initial.col}, {self.initial.row}) -> ({self.final.col}, {self.final.row})"

    def __eq__(self, other):
        return self.initial == other.initial and self.final == other.final
