import random
from constants import *
from move import Move
from square import Square
from piece import Piece, PieceColor
import numpy as np


class Board:
    def __init__(self, players: list[PieceColor]):
        self.squares = [[0] * ROWS for _ in range(COLS)]
        self.last_move = None
        self.players = players
        self.player_captured_flags = {player: False for player in self.players}
        self.number_of_players = len(self.players)
        if self.number_of_players == 2:
            rotate_grid_by = 2
        elif self.number_of_players > 2:
            rotate_grid_by = 1
        self.grid = {
            player: np.rot90(BASE_GRID, idx * rotate_grid_by) + idx * 100
            for idx, player in enumerate(self.players)
        }
        self.alias_to_row_col = {}
        for player in self.players:
            for row in range(ROWS):
                for col in range(COLS):
                    self.alias_to_row_col[self.grid[player][row, col]] = (row, col)
        self.row_col_to_alias = {player: {} for player in self.players}
        for player in self.players:
            for row in range(ROWS):
                for col in range(COLS):
                    self.row_col_to_alias[player][(row, col)] = self.grid[player][
                        row, col
                    ]
        self._create()
        for player in self.players:
            self._add_pieces(player)
        self.roll = None

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final
        enemy_pieces = self.squares[final.row][final.col].get_enemy_pieces(piece.color)
        move_length = (
            self.row_col_to_alias[piece.color][(final.row, final.col)]
            - self.row_col_to_alias[piece.color][(initial.row, initial.col)]
        )
        # Move piece to final position
        self.squares[initial.row][initial.col].remove_piece(piece)
        self.squares[final.row][final.col].add_piece(piece)
        piece.move(move_length)
        self.roll.remove(move_length)
        # Capture
        if not self.squares[final.row][final.col].is_safe_house():
            for enemy_piece in enemy_pieces:
                home_row, home_col = self.get_alias_to_row_col(
                    enemy_piece.home_position
                )
                self.squares[final.row][final.col].remove_piece(enemy_piece)
                self.squares[home_row][home_col].add_piece(enemy_piece)
                self.player_captured_flags[piece.color] = True
                enemy_piece.moved = False
                enemy_piece.return_to_home()
                self.kawade()

        piece.moved = True
        piece.clear_moves()

        self.last_move = (piece, move)

    def valid_move(self, piece: Piece, move: Move):
        return move in piece.moves

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row=row, col=col)

    def _add_pieces(self, color: PieceColor):
        home_alias = PieceColor[color].value
        home_square = np.where(self.grid[color] == home_alias * 100)
        self.squares[home_square[0][0]][home_square[1][0]] = Square(
            row=home_square[0][0],
            col=home_square[1][0],
            pieces=[Piece(color) for _ in range(PIECES_PER_PLAYER)],
        )

    def set_capture_flag(self, player: PieceColor):
        self.player_captured_flags[player] = True

    def get_alias_to_row_col(self, alias):
        return self.alias_to_row_col[alias]

    def calc_moves(self, piece: Piece, row: int, col: int):
        if piece.is_fruit():
            return
        piece.clear_moves()
        color = piece.color
        can_go_till = (
            piece.fruit_position
            if self.player_captured_flags[color]
            else piece.final_outer_position
        )
        new_positions = [
            piece.position + move
            for move in self.roll
            if piece.position + move <= can_go_till
        ]
        for pos in new_positions:
            final_row, final_col = self.get_alias_to_row_col(pos)
            if (
                (pos % 100) <= PLACES_BEFORE_INNER  # if still in the outer loop
                and (  # The final position
                    # Either needs be empty or contain an enemy piece
                    self.squares[final_row][final_col].isempty_or_enemy(piece.color)
                    # Or should be a safe house
                    or self.squares[final_row][final_col].is_safe_house()
                )
            ) or (pos % 100 > PLACES_BEFORE_INNER):
                piece.add_move(
                    Move(Square(row=row, col=col), Square(row=final_row, col=final_col))
                )

    def kawade(self):
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