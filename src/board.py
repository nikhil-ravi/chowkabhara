from typing import Optional, Tuple
from constants import *
from move import Move
from square import InvalidAliasException, Square
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
        self.enemy_piece_with_player_tied_piece = {
            player: [] for player in self.players
        }

    def _create_squares(self):
        """Generate the 49 squares (7 rows and 7 columns) on the game board.
        Each square gets a row and a column. (0, 0) is at the top left of the board."""
        self.squares = [[0] * ROWS for _ in range(COLS)]
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row=row, col=col)

    def _generate_player_paths(self):
        """Generates a Player-keyed dictionary of a player's path. The value is a
        2d-array of size ROWS x COLS, where grid[row, col] indicates the alias of the
        board square that it is on.
        For example, Player 1's (RED) grid will look like this::
            [
                [15, 14, 13, 12, 11, 10, 9],
                [16, 28, 29, 30, 31, 32, 8],
                [17, 27, 42, 43, 44, 33, 7],
                [18, 26, 41, 48, 45, 34, 6],
                [19, 25, 40, 47, 46, 35, 5],
                [20, 24, 39, 38, 37, 36, 4],
                [21, 22, 23,  0,  1,  2, 3],
            ]

        where 0 is their starting position and the path follows the squares labeled
        1, 2, 3, and so on.

        Player 2's grid is rotated 180º (when there 2 players and 90º when there
        are more than two players). When there are only two players, it takes the
        following form::
            [
                [103, 102, 101, 100, 123, 122, 121],
                [104, 136, 137, 138, 139, 124, 120],
                [105, 135, 146, 147, 140, 125, 119],
                [106, 134, 145, 148, 141, 126, 118],
                [107, 133, 144, 143, 142, 127, 117],
                [108, 132, 131, 130, 129, 128, 116],
                [109, 110, 111, 112, 113, 114, 115]
            ]

        Here, player 2 starts at 100 and follows the squares labeled 101, 102, and
        so on.
        """
        if self.number_of_players == 2:
            rotate_grid_by = 2
        elif self.number_of_players > 2:
            rotate_grid_by = 1
        self.grid = {
            player: np.rot90(BASE_GRID, idx * rotate_grid_by) + idx * GRID_OFFSET
            for idx, player in enumerate(self.players)
        }

    def _generate_alias_to_row_col(self):
        """Should be called only after the invocation of self._generate_player_paths().
        This method generates a map from a squares alias to its (row, col) position
        on the board. Since different player's alias for a square is different,
        this is a many to one mapping.

        For example, square 0 for player 1 is square 112 for player 2 in a two player game,
        both 0 and 112 point to the square at (6,3)."""
        self.alias_to_row_col = {}
        for player in self.players:
            for row in range(ROWS):
                for col in range(COLS):
                    self.alias_to_row_col[self.grid[player][row, col]] = (row, col)

    def _generate_row_col_to_alias(self):
        """Should be called only after the invocation of self._generate_player_paths().
        This method generates a map Player-keyed map of what its alias for a square
        at (row, col) is.

        For example, the square at (6, 3) is square 0 for player 1 and 112 for
        player 2 in a two player game.
        """
        self.row_col_to_alias = {player: {} for player in self.players}
        for player in self.players:
            for row in range(ROWS):
                for col in range(COLS):
                    self.row_col_to_alias[player][(row, col)] = self.grid[player][
                        row, col
                    ]

    def _add_pieces(self):
        """Calls the _add_pieces_for_player method for each player."""
        for player in self.players:
            self._add_pieces_for_player(player)

    def _add_pieces_for_player(self, color: PieceColor, testing: bool = False):
        """For the given player, add PIECES_PER_PLAYER number of Pieces to its
        initial square.

        Args:
            color (PieceColor): The Player's color.
            testing (bool, optional): Used to add pieces during debugging. Defaults to False.
        """
        home_alias = PieceColor[color].value
        home_square = np.where(self.grid[color] == home_alias * GRID_OFFSET)
        self.squares[home_square[0][0]][home_square[1][0]] = Square(
            row=home_square[0][0],
            col=home_square[1][0],
            pieces=[Piece(color) for _ in range(PIECES_PER_PLAYER)],
        )
        # Testing
        if testing:
            if color == "Red":
                self.squares[1][1] = Square(
                    row=1,
                    col=1,
                    pieces=[
                        TiedPiece(color, 28, [Piece(color), Piece(color)]),
                    ],
                )  # //TODO
                self.set_capture_flag(color)
            if color == "Green":
                # self.squares[2][1] = Square(
                #     row=2,
                #     col=1,
                #     pieces=[TiedPiece(color, 135, [Piece(color), Piece(color)])],
                # )  # //TODO
                self.squares[5][1] = Square(
                    row=5, col=1, pieces=[Piece(color), Piece(color)]
                )  # //TODO
                self.squares[5][1].pieces[0].position = 132
                self.squares[5][1].pieces[1].position = 132

                # self.squares[2][5] = Square(row=2, col=5, pieces=[Piece(color)])  # //TODO
                # self.squares[2][5].pieces[0].position = 125

                # tempPiece = Piece(color)
                # tempPiece.position = 132
                # self.squares[5][1].pieces.append(tempPiece)  # //TODO
                self.set_capture_flag(color)

    def move(self, piece: Piece | TiedPiece, move: Move):
        """Given a piece and a move, this method moves the piece by:
        1. Removing the piece from its current square's pieces vector,
        2. Adding the piece to the move's final square's pieces vector,
        3. Updating the piece's position element to the player's alias of the final square,
        4. Updating the roll vector by removing the move from it
        5. If captures are possible, it will remove other players' pieces from the final square,
        move those pieces to their home position, and update their position accordingly.

        If there is a possibility to tie two pieces together, this method handles that as well.

        Args:
            piece (Piece | TiedPiece): The Piece to move.
            move (Move): The move to be applied to the piece.
        """
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
            if self.squares[final.row][final.col].has_enemy_tied_piece(piece.color):
                piece.set_with_enemy_tied_piece()
                for enemypiece in self.squares[final.row][final.col].pieces:
                    if enemypiece.name == "TiedPiece":
                        if self.enemy_piece_with_player_tied_piece[enemypiece.color]:
                            self.enemy_piece_with_player_tied_piece[
                                enemypiece.color
                            ].append(piece)
                        else:
                            self.enemy_piece_with_player_tied_piece[
                                enemypiece.color
                            ] = [piece]
            move_length_to_remove = (
                2 * move_length if piece.name == "TiedPiece" else move_length
            )
            self.roll.remove(move_length_to_remove)
        else:
            # Remove the piece
            self.squares[initial.row][initial.col].remove_piece(piece)
            # Find the other piece to tie with and remove that too
            other_piece = self.squares[initial.row][
                initial.col
            ].get_other_single_team_piece(piece)
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
        if not self.squares[final.row][final.col].is_safe_house:
            enemy_pieces = self.squares[final.row][final.col].get_enemy_pieces(
                piece.color
            )
            for enemy_piece in enemy_pieces:
                if not (enemy_piece.name == "TiedPiece" and piece.name == "Piece"):
                    home_row, home_col = self.get_alias_to_row_col(
                        enemy_piece.home_position
                    )
                    self.squares[final.row][final.col].remove_piece(enemy_piece)
                    if enemy_piece.name == "TiedPiece":
                        for enemy_piece_component_piece in enemy_piece.pieces:
                            self.squares[home_row][home_col].add_piece(
                                enemy_piece_component_piece
                            )
                    else:
                        self.squares[home_row][home_col].add_piece(enemy_piece)
                    self.player_captured_flags[piece.color] = True
                    enemy_piece.moved = False
                    enemy_piece.return_to_home()
                    self.kawade()
        # If a Single Piece is on a square with an enemy TiedPiece, then it can
        # be captured when the TiedPiece moves.
        if piece.name == "TiedPiece" and (
            not self.squares[initial.row][initial.col].is_safe_house
        ):
            enemy_pieces = self.squares[initial.row][initial.col].get_enemy_pieces(
                piece.color
            )
            for enemy_piece in enemy_pieces:
                home_row, home_col = self.get_alias_to_row_col(
                    enemy_piece.home_position
                )
                self.squares[initial.row][initial.col].remove_piece(enemy_piece)
                self.squares[home_row][home_col].add_piece(enemy_piece)
                self.player_captured_flags[piece.color] = True
                enemy_piece.moved = False
                enemy_piece.return_to_home()

        piece.moved = True
        piece.clear_moves()

    def valid_move(self, piece: Piece | TiedPiece, move: Move) -> bool:
        """Checks whether a move is valid.

        Args:
            piece (Piece | TiedPiece): The Piece to move.
            move (Move): The move to be applied to the piece.

        Returns:
            bool: Whether the move is valid.
        """
        return move in piece.moves

    def set_capture_flag(self, player: PieceColor):
        """Sets the a player's capture flag enabling them to move to the inner
        squares.

        Args:
            player (PieceColor): The player whose capture flag is to be set.
        """
        self.player_captured_flags[player] = True

    def get_alias_to_row_col(self, alias: int) -> Tuple[int, int]:
        """The the row, col of the square with the given alias.

        Args:
            alias (int): The square's alias.

        Raises:
            InvalidAliasException: Raised when an alias is not registered.

        Returns:
            Tuple[int, int]: The (row, col) of the square.
        """
        if alias not in self.alias_to_row_col:
            raise InvalidAliasException
        else:
            return self.alias_to_row_col[alias]

    def can_move(self, player) -> bool:
        return True

    def calc_moves(self, piece: Piece):
        """Calculate which of moves from the roll the given Piece at row and col
        can undertake. It first clears the piece's moves vector and then populates
        it with the latest moves available.

        Args:
            piece (Piece): The piece whose moves are to be calculated.
        """
        piece.clear_moves()
        if piece.is_fruit():
            return
        row, col = self.get_alias_to_row_col(piece.position)
        color = piece.color
        if piece.name == "Piece" and not piece.with_enemy_tied_piece:
            can_tie = (
                True
                if self.squares[row][col].get_other_single_team_piece(piece)
                and piece.name == "Piece"
                and not self.squares[row][col].is_safe_house
                else False
            )
            can_go_till = (
                piece.fruit_position
                if self.player_captured_flags[color]
                else piece.final_outer_position
            )
            for places in sorted(self.roll):
                if (
                    self.intermediate_squares_have_enemy_tied_pieces(piece, places)
                    == False
                ):
                    pos = piece.position + places
                    if pos <= can_go_till:
                        final_row, final_col = self.get_alias_to_row_col(pos)
                        if (
                            (pos % GRID_OFFSET)
                            <= PLACES_BEFORE_INNER  # if still in the outer loop
                            and (  # The final position
                                # Either needs be empty or contain an enemy piece
                                self.squares[final_row][final_col].isempty_or_enemy(
                                    piece.color
                                )
                                # Or should be a safe house
                                or self.squares[final_row][final_col].is_safe_house
                            )
                        ) or (pos % GRID_OFFSET > PLACES_BEFORE_INNER):
                            move_to_add = Move(
                                Square(row=row, col=col),
                                Square(row=final_row, col=final_col),
                            )
                            piece.add_move(move_to_add)
                    if (
                        places == 2
                        and can_tie
                        and (piece.position % GRID_OFFSET > PLACES_BEFORE_INNER)
                    ):
                        final_row, final_col = self.get_alias_to_row_col(
                            piece.position + 1
                        )
                        final_Square = Square(row=final_row, col=final_col)
                        if not final_Square.is_safe_house:
                            move_to_add = Move(
                                initial=Square(row=row, col=col),
                                final=Square(row=final_row, col=final_col),
                                tying_move=True,
                            )
                            piece.add_move(move_to_add)
                else:
                    break
        if piece.name == "TiedPiece":
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

    def intermediate_squares_have_enemy_tied_pieces(
        self, piece: Piece, places: int
    ) -> bool:
        """Checks whether there are any enemy TiedPieces between the piece's location
        and its intended final location.

        Args:
            piece (Piece): The piece whose path should be checked.
            places (int): The increment to the piece's position that is to be checked.

        Returns:
            bool: True if there is a enemy TiedPiece between the piece's position
            and its position advanced by places.
        """
        for intermediate_place in range(1, places):
            intermediate_row, intermediate_col = self.get_alias_to_row_col(
                intermediate_place + piece.position
            )
            if (intermediate_row, intermediate_col) not in SAFE_HOUSES and self.squares[
                intermediate_row
            ][intermediate_col].has_enemy_tied_piece(piece.color):
                print("Here")
                intermediate_Tied_Piece = [
                    Tied_Piece
                    for Tied_Piece in self.squares[intermediate_row][
                        intermediate_col
                    ].pieces
                    if Tied_Piece.color != piece.color
                ][0]
                if not self.squares[intermediate_row][
                    intermediate_col
                ].has_single_team_piece(intermediate_Tied_Piece.color):
                    print("3Here")
                    return True
        return False

    def kawade(self, testing: bool = False):
        """This method generates the rolls for the current player and adds it to the
        roll vector of the Board instance. If a player rolls 4, 6, or 12, the player
        gets to re roll.

        Args:
            testing (bool, optional): Used during testing to generate a given roll.
                Defaults to False.
        """
        if not testing:
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
            self.roll = [2]

    def clear_enemy_pieces_with_player_tied_piece(self, color: PieceColor):
        """Clear the flag on all enemy pieces that are on the same square the
        TiedPieces of the given color.

        Args:
            color (PieceColor): The player's color
        """
        if self.enemy_piece_with_player_tied_piece[color]:
            for piece in self.enemy_piece_with_player_tied_piece[color]:
                piece.clear_with_enemy_tied_piece()
            self.enemy_piece_with_player_tied_piece[color] = None

    def has_player_finished(self, player: PieceColor) -> bool:
        """Checks whether all of the given player's pieces are in the finish square.

        Args:
            player (PieceColor): The player's color.

        Returns:
            bool: Whether all of the player's pieces are in the finish square.
        """
        fruited_pieces = 0
        for piece in self.squares[ROWS // 2][COLS // 2].pieces:
            if piece.color == player:
                fruited_pieces += 1 if piece.name == "Piece" else 2
        if fruited_pieces == PIECES_PER_PLAYER:
            return True
        return False
