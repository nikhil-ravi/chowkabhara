from enum import Enum
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
    def __init__(self):
        self.number_of_players = 2
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

    def show_bg(self, surface):
        theme = self.config.theme
        surface.fill(theme.value.light)
        self._draw_lines(surface, theme.value.dark)
        self._draw_safe_houses(surface, theme.value.dark)
        self._draw_letter_markings(surface, theme.value.dark)

    def show_pieces(self, surface):
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

    def show_hover(self, surface):
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
        if not self.board.roll:
            self.next_player_id += 1
            self.next_player_id %= self.number_of_players
            self.next_player = self.players[self.next_player_id]

    def next_action(self):
        if self.current_stage == "ROLL":
            self.board.roll()
        elif self.current_stage == "MAKE_MOVE":
            self.wait()
        else:
            self.next_turn()

    def wait(self):
        self.current_stage = "MAKE_MOVE"

    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]

    def change_theme(self):
        self.config.change_theme()

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()

    def _draw_lines(self, surface, line_color):
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

    def _draw_safe_houses(self, surface, line_color):
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

    def _draw_letter_markings(self, surface, font_color):
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

    def show_roll(self, surface):
        theme = self.config.theme
        lbl = self.config.font.render(
            ",".join([str(roll) for roll in self.board.roll]), 5, theme.value.dark
        )
        lbl_pos = (3 * SQSIZE, 3 * SQSIZE)
        # blit
        surface.blit(lbl, lbl_pos)

    def show_moves(self, surface):
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

    def draw_rect_alpha(self, surface, color, rect):
        shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
        pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
        surface.blit(shape_surf, rect)


class GameStage(Enum):
    ROLL = 1
    MAKE_MOVE = 2
    NEXT_TURN = 3
