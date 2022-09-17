import sys
import time
import pygame
from constants import *
from game import Game
from move import Move
from square import Square
from piece import PieceColor

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chowka Bhara")
screen.fill(BG_COLOR)


class Main:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chowka Bhara")
        self.game = Game(number_of_players=2)  # Can be between 2 and 4 players.

    def mainloop(self):
        """The main loop of the game."""
        screen = self.screen
        game = self.game
        board = self.game.board
        dragger = self.game.dragger
        pygame.display.set_caption(f"Chowka Bhara: Roll for player {game.next_player}")

        while True:
            game.show_bg(screen)
            game.show_moves(screen)
            game.show_pieces(screen)

            if dragger.dragging:
                dragger.update_blit(screen)
            if game.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if game.current_stage == "ROLL":
                            board.kawade()
                            pygame.display.set_caption(
                                f"Chowka Bhara: Player {game.next_player} - Make Move! {board.roll}"
                            )
                            if board.can_move(game.next_player):
                                game.current_stage = "MAKE_MOVE"
                            else:
                                board.roll = []
                                game.next_turn()
                                game.current_stage = "ROLL"
                                pygame.display.set_caption(
                                    f"Chowka Bhara: Player has no moves. Roll for player {game.next_player}"
                                )
                        elif game.current_stage == "MAKE_MOVE":
                            dragger.update_mouse(event.pos)
                            clicked_row = dragger.mouseY // SQSIZE
                            clicked_col = dragger.mouseX // SQSIZE
                            if board.squares[clicked_row][clicked_col].has_pieces():
                                for piece in board.squares[clicked_row][
                                    clicked_col
                                ].pieces:
                                    if piece.texture_rect.collidepoint(event.pos):
                                        selected_piece = piece
                                        if selected_piece.color == game.next_player:
                                            board.calc_moves(selected_piece)
                                            dragger.save_initial(event.pos)
                                            dragger.drag_piece(selected_piece)
                                            game.show_bg(screen)
                                            game.show_moves(screen)
                                            game.show_pieces(screen)
                    elif event.type == pygame.MOUSEMOTION:
                        if game.current_stage == "MAKE_MOVE":
                            motion_row = event.pos[1] // SQSIZE
                            motion_col = event.pos[0] // SQSIZE
                            game.set_hover(motion_row, motion_col)
                            if dragger.dragging:
                                dragger.update_mouse(event.pos)
                                game.show_bg(screen)
                                game.show_moves(screen)
                                game.show_pieces(screen)
                                game.show_hover(screen)
                                dragger.update_blit(screen)
                    elif event.type == pygame.MOUSEBUTTONUP:
                        if game.current_stage == "MAKE_MOVE" and dragger.dragging:
                            dragger.update_mouse(event.pos)
                            released_row = dragger.mouseY // SQSIZE
                            released_col = dragger.mouseX // SQSIZE
                            initial = Square(
                                row=dragger.initial_row, col=dragger.initial_col
                            )
                            final = Square(row=released_row, col=released_col)
                            move = Move(initial=initial, final=final)

                            if board.valid_move(dragger.piece, move):
                                move = dragger.get_move_from_initial_final(
                                    move.initial, move.final
                                )
                                if board.squares[released_row][
                                    released_col
                                ].has_enemy_piece(game.next_player) and (
                                    not board.squares[released_row][
                                        released_col
                                    ].is_safe_house
                                ):
                                    captured = True
                                else:
                                    captured = False
                                board.move(dragger.piece, move)
                                player_has_finished = board.has_player_finished(
                                    game.next_player
                                )
                                if player_has_finished:
                                    game.player_has_finished.append(
                                        PieceColor[game.next_player].value
                                    )
                                    pygame.display.set_caption(
                                        f"Chowka Bhara: Player {game.next_player} has finished."
                                    )
                                # if not final.is_safe_house:
                                game.play_sound(captured)
                                game.show_bg(screen)
                                game.show_pieces(screen)
                                game.next_turn()
                                if game.is_over():
                                    game.running = False
                                    game.current_stage = "GAME_OVER"
                                    pygame.display.set_caption(
                                        f"Chowka Bhara: Game Over"
                                    )

                        if len(board.roll) == 0:
                            game.current_stage = "ROLL"
                            pygame.display.set_caption(
                                f"Chowka Bhara: Roll for player {game.next_player}"
                            )
                        else:
                            pygame.display.set_caption(
                                f"Chowka Bhara: Player {game.next_player} - Make Move! {board.roll}"
                            )
                        dragger.undrag_piece()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                        board.roll = []
                        game.next_turn()
                        game.current_stage = "ROLL"
                        pygame.display.set_caption(
                            f"Chowka Bhara: Player skipped. Roll for player {game.next_player}"
                        )
            else:
                pygame.display.set_caption(f"Chowka Bhara: Game Over")
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
            pygame.display.update()


main = Main()
main.mainloop()
