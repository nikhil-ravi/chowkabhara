from enum import Enum
from typing import Tuple
import pygame
from constants import (
    SQSIZE,
    IMG_CENTERS,
    ROWS,
    COLS,
    SAFE_HOUSES,
    LINE_WIDTH,
    HEIGHT,
    WIDTH,
)
from board import Board
from dragger import Dragger
from piece import PieceColor
from config import Config
from square import Square
import numpy as np


class Game:
    """The main game class."""

    def __init__(self, number_of_players: int = 2):
        self.number_of_players = number_of_players
        self.players = list(PieceColor.__members__.keys())[: self.number_of_players]
        self.next_player_id = 0
        self.next_player = self.players[self.next_player_id]
        self.game_stages = list(GameStage.__members__.keys())
        self.game_stage_id = 0
        self.current_stage = self.game_stages[self.game_stage_id]
        self.hovered_sqr = None
        self.board = Board(players=self.players)
        self.dragger = Dragger()
        self.config = Config()
        self.player_has_finished = []
        self.running = True

    def show_bg(self, surface: pygame.Surface):
        """Shows the background on the given pygame surface.

        Args:
            surface (pygame.Surface): The pygame surface to draw the background on.
        """
        theme = self.config.theme
        surface.fill(theme.value.light)
        self._draw_lines(surface, theme.value.dark)
        self._draw_safe_houses(surface, theme.value.dark)
        self._draw_letter_markings(surface, theme.value.dark)

    def show_pieces(self, surface: pygame.Surface):
        """Draws the piece on the given surface at their respective positions.

        Args:
            surface (pygame.Surface): The pygame surface to draw the pieces on.
        """
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_pieces:
                    pieces = self.board.squares[row][col].pieces

                    for piece_idx, piece in enumerate(pieces):
                        if piece is not self.dragger.piece:
                            piece.set_texture(size=80)
                            img = pygame.image.load(piece.texture)
                            img = pygame.transform.rotozoom(
                                img, 0, 1 / np.sqrt(len(pieces))
                            )
                            img_center = (
                                col * SQSIZE + IMG_CENTERS[len(pieces)][piece_idx][0],
                                row * SQSIZE + IMG_CENTERS[len(pieces)][piece_idx][1],
                            )
                            piece.texture_rect = img.get_rect(center=img_center)
                            surface.blit(img, piece.texture_rect)

    def show_hover(self, surface: pygame.Surface):
        """Shows the hovered square.

        Args:
            surface (pygame.Surface): The surface to show the hovered square.
        """
        if self.hovered_sqr:
            # color
            color = (180, 180, 180)
            # rect
            rect = (
                self.hovered_sqr.col * SQSIZE,
                self.hovered_sqr.row * SQSIZE,
                SQSIZE,
                SQSIZE,
            )
            # blit
            pygame.draw.rect(surface, color, rect, width=3)

    def next_turn(self):
        """If the current player has made all their moves (the board's roll vector
        is empty), this method changes the turn to the next player in the
        :py:class:`piece.PieceColor` enum.
        """
        if not self.board.roll:
            self.board.clear_enemy_pieces_with_player_tied_piece(self.next_player)
            self.next_player_id = (self.next_player_id + 1) % self.number_of_players
            while self.next_player_id in self.player_has_finished:
                self.next_player_id = (self.next_player_id + 1) % self.number_of_players
            self.next_player = self.players[self.next_player_id]

    def next_action(self):
        """Change to the next action."""
        if self.current_stage == "ROLL":
            self.board.roll()
        elif self.current_stage == "MAKE_MOVE":
            self.current_stage = "MAKE_MOVE"
        else:
            self.next_turn()

    def set_hover(self, row: int, col: int):
        """Set the hovered square to the square at row and col.

        Args:
            row (int): The row of the square.
            col (int): The col of the square.
        """
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        """Changes the game theme."""
        self.config.change_theme()

    def play_sound(self, captured: bool = False):
        """Play the move sound when a piece is moved and the capture sound when
        a piece is captured.

        Args:
            captured (bool, optional): Whether a piece was captured. Defaults to False.
        """
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        """Resets the game."""
        self.__init__()

    def _draw_lines(self, surface: pygame.Surface, line_color: Tuple[int, int, int]):
        """Draw the lines on the board to represent the squares.

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
            line_color (Tuple[int, int, int]): The line color supplied as R,G,B values.
        """
        for col in range(COLS + 1):
            pygame.draw.line(
                surface,
                line_color,
                (col * SQSIZE, 0),
                (col * SQSIZE, HEIGHT),
                LINE_WIDTH,
            )
        for row in range(ROWS + 1):
            pygame.draw.line(
                surface,
                line_color,
                (0, row * SQSIZE),
                (WIDTH, row * SQSIZE),
                LINE_WIDTH,
            )

    def _draw_safe_houses(
        self, surface: pygame.Surface, line_color: Tuple[int, int, int]
    ):
        """Draw the lines on the board to represent the safe house squares.

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
            line_color (Tuple[int, int, int]): The line color supplied as R,G,B values.
        """
        for (row, col) in SAFE_HOUSES:
            pygame.draw.line(
                surface,
                line_color,
                (col * SQSIZE, row * SQSIZE),
                ((col + 1) * SQSIZE, (row + 1) * SQSIZE),
                LINE_WIDTH,
            )
            pygame.draw.line(
                surface,
                line_color,
                ((col + 1) * SQSIZE, row * SQSIZE),
                (col * SQSIZE, (row + 1) * SQSIZE),
                LINE_WIDTH,
            )

    def _draw_letter_markings(
        self, surface: pygame.Surface, font_color: Tuple[int, int, int]
    ):
        """Draw the column and row markers on the board.

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
            font_color (Tuple[int, int, int]): The font color supplied as R,G,B values.
        """
        for row in range(ROWS):
            for col in range(COLS):
                if col == 0:
                    # label
                    lbl = self.config.font.render(str(ROWS - row), 1, font_color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    # blit
                    surface.blit(lbl, lbl_pos)

                # col coordinates
                if row == 6:
                    # label
                    lbl = self.config.font.render(
                        Square.get_alphacol(col), 1, font_color
                    )
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    # blit
                    surface.blit(lbl, lbl_pos)

    def show_roll(self, surface: pygame.Surface):
        """Show the roll the current player has.

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
        """
        theme = self.config.theme
        lbl = self.config.font.render(
            ",".join([str(roll) for roll in self.board.roll]), 5, theme.value.dark
        )
        lbl_pos = (3 * SQSIZE, 3 * SQSIZE)
        # blit
        surface.blit(lbl, lbl_pos)

    def show_moves(self, surface: pygame.Surface):
        """Show the moves of the current :meth:`src.dragger.piece`

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
        """
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # loop all valid moves
            for move in piece.moves:
                # color
                color = (*theme.value.dark, 100)
                # rect
                rect = (
                    move.final.col * SQSIZE,
                    move.final.row * SQSIZE,
                    SQSIZE,
                    SQSIZE,
                )
                # blit
                self.draw_rect_alpha(surface, color, rect)

    def draw_rect_alpha(
        self,
        surface: pygame.Surface,
        color: Tuple[int, int, int, int],
        rect: Tuple[int, int, int, int],
    ):
        """Draw a rectangle with the given color and alpha.

        Args:
            surface (pygame.Surface): The pygame surface to draw on.
            color (Tuple[int, int, int, int]): The (R,G,B) color and alpha for the rectangle.
            rect (Tuple[int, int, int, int]): The rectangle to draw.
        """
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
        surface.blit(shape_surf, rect)

    def is_over(self):
        return (
            True
            if (len(self.player_has_finished) == (self.number_of_players - 1))
            else False
        )


class GameStage(Enum):
    """Enumeration of the different stages of the game."""

    ROLL = 1
    MAKE_MOVE = 2
    NEXT_TURN = 3
