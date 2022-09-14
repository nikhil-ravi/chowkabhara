from constants import *
from move import Move
from square import Square
from piece import Piece, PieceColor, TiedPiece
import numpy as np


class Board:
    def __init__(self, players: list[PieceColor]):
        self._create_squares()

        self.players = players
        self.player_captured_flags = {player: False for player in self.players}
        self.number_of_players = len(self.players)
        self._generate_player_paths()

        self._generate_alias_to_row_col()

        self._generate_row_col_to_alias()
        self._add_pieces()

        self.roll = None

    def _create_squares(self):
        self.squares = [[0] * ROWS for _ in range(COLS)]
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row=row, col=col)

    def _generate_player_paths(self):
        if self.number_of_players == 2:
            rotate_grid_by = 2
        elif self.number_of_players > 2:
            rotate_grid_by = 1
        self.grid = {
            player: np.rot90(BASE_GRID, idx * rotate_grid_by) + idx * GRID_OFFSET
            for idx, player in enumerate(self.players)
        }

    def _generate_alias_to_row_col(self):
        self.alias_to_row_col = {}
        for player in self.players:
            for row in range(ROWS):
                for col in range(COLS):
                    self.alias_to_row_col[self.grid[player][row, col]] = (row, col)

    def _generate_row_col_to_alias(self):
        self.row_col_to_alias = {player: {} for player in self.players}
        for player in self.players:
            for row in range(ROWS):
                for col in range(COLS):
                    self.row_col_to_alias[player][(row, col)] = self.grid[player][row, col]

    def _add_pieces(self):
        for player in self.players:
            self._add_pieces_for_player(player)

    def _add_pieces_for_player(self, color: PieceColor):
        home_alias = PieceColor[color].value
        home_square = np.where(self.grid[color] == home_alias * GRID_OFFSET)
        self.squares[home_square[0][0]][home_square[1][0]] = Square(
            row=home_square[0][0],
            col=home_square[1][0],
            pieces=[Piece(color) for _ in range(PIECES_PER_PLAYER)],
        )
        # Testing
        if color == "Red":
            self.squares[3][1] = Square(
                row=3, col=1, pieces=[TiedPiece(color, 26, [Piece(color), Piece(color)])]
            )  # //TODO
        if color == "Green":
            self.squares[0][6] = Square(row=0, col=6, pieces=[Piece(color)])  # //TODO
            self.squares[0][6].pieces[0].position = 121

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final
        tying_move = move.tying_move
        if not tying_move:
            move_length = (
                self.row_col_to_alias[piece.color][(final.row, final.col)]
                - self.row_col_to_alias[piece.color][(initial.row, initial.col)]
            )
            # Move piece to final position
            self.squares[initial.row][initial.col].remove_piece(piece)
            self.squares[final.row][final.col].add_piece(piece)
            piece.move(move_length)
            move_length_to_remove = 2 * move_length if piece.name == "TiedPiece" else move_length
            self.roll.remove(move_length_to_remove)
        else:
            # Remove the piece
            self.squares[initial.row][initial.col].remove_piece(piece)
            # Find the other piece to tie with and remove that too
            other_piece = self.squares[initial.row][initial.col].get_other_single_team_piece(piece)
            self.squares[initial.row][initial.col].remove_piece(other_piece)
            self.squares[final.row][final.col].add_piece(
                TiedPiece(
                    piece.color,
                    self.row_col_to_alias[piece.color][(final.row, final.col)],
                    [piece, other_piece],
                )
            )
            self.roll.remove(2)
        # Capture
        if not self.squares[final.row][final.col].is_safe_house():
            enemy_pieces = self.squares[final.row][final.col].get_enemy_pieces(piece.color)
            for enemy_piece in enemy_pieces:
                if not (enemy_piece.name == "TiedPiece" and piece.name == "Piece"):
                    home_row, home_col = self.get_alias_to_row_col(enemy_piece.home_position)
                    self.squares[final.row][final.col].remove_piece(enemy_piece)
                    self.squares[home_row][home_col].add_piece(enemy_piece)
                    self.player_captured_flags[piece.color] = True
                    enemy_piece.moved = False
                    enemy_piece.return_to_home()
                    self.kawade()

        piece.moved = True
        piece.clear_moves()

    def valid_move(self, piece: Piece, move: Move):
        return move in piece.moves

    def set_capture_flag(self, player: PieceColor):
        self.player_captured_flags[player] = True

    def get_alias_to_row_col(self, alias):
        return self.alias_to_row_col[alias]

    def calc_moves(self, piece: Piece, row: int, col: int):
        if piece.is_fruit():
            return
        piece.clear_moves()
        row, col = self.get_alias_to_row_col(piece.position)
        color = piece.color
        if piece.name == "Piece":
            can_tie = True if self.squares[row][col].has_single_team_piece(color) and piece.name == "Piece" else False
            can_go_till = piece.fruit_position if self.player_captured_flags[color] else piece.final_outer_position
            for places in self.roll:
                pos = piece.position + places
                if pos <= can_go_till:
                    final_row, final_col = self.get_alias_to_row_col(pos)
                    if (
                        (pos % GRID_OFFSET) <= PLACES_BEFORE_INNER  # if still in the outer loop
                        and (  # The final position
                            # Either needs be empty or contain an enemy piece
                            self.squares[final_row][final_col].isempty_or_enemy(piece.color)
                            # Or should be a safe house
                            or self.squares[final_row][final_col].is_safe_house()
                        )
                    ) or (pos % GRID_OFFSET > PLACES_BEFORE_INNER):
                        piece.add_move(
                            Move(
                                Square(row=row, col=col),
                                Square(row=final_row, col=final_col),
                            )
                        )
                if places == 2 and can_tie and (piece.position % GRID_OFFSET > PLACES_BEFORE_INNER):
                    final_row, final_col = self.get_alias_to_row_col(piece.position + 1)
                    piece.add_move(
                        Move(
                            initial=Square(row=row, col=col),
                            final=Square(row=final_row, col=final_col),
                            tying_move=True,
                        )
                    )
        if piece.name == "TiedPiece":
            piece.clear_moves()
            can_go_till = piece.fruit_position
            for places in self.roll:
                if places % 2 == 0:
                    pos = piece.position + places // 2
                    if pos <= can_go_till:
                        final_row, final_col = self.get_alias_to_row_col(pos)
                        move_to_add = Move(
                            Square(row=row, col=col),
                            Square(row=final_row, col=final_col),
                        )
                        piece.add_move(move_to_add)

    def kawade(self, test: bool = False):
        if not test:
            roll = np.random.choice(
                a=[1, 2, 3, 4, 5, 6, 12],
                p=[6 / 64, 15 / 64, 20 / 64, 15 / 64, 6 / 64, 1 / 64, 1 / 64],
            )
            if self.roll:
                self.roll.append(roll)
            else:
                self.roll = [roll]
            while self.roll[-1] in [4, 6, 12]:
                self.roll.append(
                    np.random.choice(
                        a=[1, 2, 3, 4, 5, 6, 12],
                        p=[6 / 64, 15 / 64, 20 / 64, 15 / 64, 6 / 64, 1 / 64, 1 / 64],
                    )
                )
        else:
            self.roll = [12, 4, 4, 2]
