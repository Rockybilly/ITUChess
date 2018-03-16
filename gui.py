import sys
import pygame
# from pygame.locals import *
from pygame import gfxdraw
from button import Button
import internals

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_GRAY = (130, 130, 130)
RED = (255, 0, 0)
DARK_RED = (155, 0, 9)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 155, 0)
SELECT_COLOR = (255, 10, 10, 210)
MOVE_COLOR = (200, 100, 100, 140)
BEST_MOVE_COLOR = (90, 90, 200, 140)


WIDTH = 1400
HEIGHT = 800


class Gui(object):
    """
    Main game class, where the main game function exists and includes other game functionalities.
    """

    def __init__(self):
        pygame.init()
        self.search_font = pygame.font.SysFont("monospace", 36)
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        # There are program states
        # menu, game,
        #
        self.program_state = "menu"
        self.analyzing = False
        self.game = None
        # Define all buttons that are going to be used
        # Inside the program, using a dictionary.
        # Format {
        #   button_name: button_object
        # }

        self.show_help = False
        self.menu_buttons = {
            # Button class (pos, text_font, text_color, text_padding, message, color, hover_color, handler_function)
            "newgameai": Button((200, 300), "monospace", 30, BLACK, 3, "NEW GAME with AI", DARK_GREEN, GREEN, self.new_game_ai),
            "testgame": Button((200, 400), "monospace", 30, BLACK, 3, "TEST GAME", DARK_GREEN, GREEN, self.test_game),
            "exit":    Button((200, 500), "monospace", 30, BLACK, 3, "QUIT", DARK_RED, RED, self.quit)
        }

        self.game_buttons = {
            "help": Button((820, 20), "monospace", 30, BLACK, 3, "Show Help", DARK_GREEN, GREEN, self.toggle_help),
            "analyze": Button((1020, 20), "monospace", 30, BLACK, 3, "Analyze", DARK_GREEN, GREEN, self.start_analysis)
        }
        
        self.board_image = pygame.image.load("chessboard.png")
        self.piece_image = pygame.image.load("piece_sprite.png")
       
    def main(self):
        """
        The function with the main loop of the game.
        """

        while True:
            self.clock.tick(30)
            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    if self.game: self.game.game_exit()
                    pygame.quit()
                    sys.exit()

                # event button 1 is the left mouse button.
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mouse_handler(pygame.mouse.get_pos())

                #print("still here.")
            self.draw_gui()

    def test_game(self):
        self.game = internals.Game(0, "test")
        self.program_state = "game"

    def new_game_ai(self):

        self.game = internals.Game(0, "ai")
        self.program_state = "game"

    @staticmethod
    def quit():
        pygame.quit()  # quits pygame
        sys.exit()

    def toggle_help(self):

        if self.show_help:
            self.game_buttons["help"] = Button((820, 20), "monospace", 30, BLACK, 3, "Show Help", DARK_GREEN, GREEN, self.toggle_help)
            self.show_help = False
        else:
            self.game_buttons["help"] = Button((820, 20), "monospace", 30, BLACK, 3, "Hide Help", DARK_GREEN, GREEN, self.toggle_help)
            self.show_help = True

    def draw_gui(self):
        """
        Method that draws all of th elements to the screen
        """

        if self.program_state == "menu":
            self.screen.fill(WHITE)
            pygame.draw.rect(self.screen, BLACK, [0, 0, WIDTH, HEIGHT], 5)
            self.draw_text((175, 75), 128, BLACK, "ITUChess")

        elif self.program_state == "game":
            self.screen.fill(WHITE)
            self.draw_board()
            text = self.search_font.render(self.game.best_move_string, True, BLACK)
            self.screen.blit(text, (WIDTH - 550, HEIGHT - 50))

        self.draw_buttons()
        pygame.display.flip()

    def draw_board(self):
        """
        The method that draws the board, all the pieces and the selected tiles on it. 
        """

        self.screen.blit(self.board_image, (0, 0))

        if self.game.best_move:
            fr, to = self.game.best_move
            self.colorize_tile(to, BEST_MOVE_COLOR)
            self.colorize_tile(fr, BEST_MOVE_COLOR)

        # Drawing the selected tile, and the legal moves of the pieces in that tile.
        if self.game.selected:
            self.colorize_tile(self.game.selected, SELECT_COLOR)
            if self.show_help:
                for move in self.game.selected_moves:
                    self.colorize_tile(move, MOVE_COLOR)
        
        for i, row in enumerate(self.game.board.grid):
            for j, piece in enumerate(row):
                if piece:

                    pos = j * 100, i * 100
                    color_padding = 0 if piece.color == "white" else 100
                    image_interval = 100

                    if piece.kind == "king":
                        self.screen.blit(self.piece_image, pos, [image_interval * 0, color_padding, image_interval, image_interval])
                    elif piece.kind == "queen":
                        self.screen.blit(self.piece_image, pos, [image_interval * 1, color_padding, image_interval, image_interval])
                    elif piece.kind == "bishop":
                        self.screen.blit(self.piece_image, pos, [image_interval * 2, color_padding, image_interval, image_interval])
                    elif piece.kind == "knight":
                        self.screen.blit(self.piece_image, pos, [image_interval * 3, color_padding, image_interval, image_interval])
                    elif piece.kind == "rook":
                        self.screen.blit(self.piece_image, pos, [image_interval * 4, color_padding, image_interval, image_interval])
                    elif piece.kind == "pawn":
                        self.screen.blit(self.piece_image, pos, [image_interval * 5, color_padding, image_interval, image_interval])

        pygame.draw.line(self.screen, BLACK, (800, 0), (800, HEIGHT), 3)

    def draw_buttons(self):

        if self.program_state == "menu":
            for button_name in self.menu_buttons:
                self.menu_buttons[button_name].draw(self.screen, pygame.mouse.get_pos())

        elif self.program_state == "game":
            for button_name in self.game_buttons:
                self.game_buttons[button_name].draw(self.screen, pygame.mouse.get_pos())

    def draw_text(self, pos, size, color, message):
        """
        Method that draws a text to the screen.
        """

        text_font = pygame.font.SysFont("Impact", size)
        self.screen.blit(text_font.render(message, 0, color), pos)

    def colorize_tile(self, tile, color):
        """
        Function to draw selected and legal move tiles.
        """

        corner1 = tile[1] * 100, tile[0] * 100
        corner2 = corner1[0] + 100, corner1[1]
        corner3 = corner1[0] + 100, corner1[1] + 100
        corner4 = corner1[0], corner1[1] + 100 

        pygame.gfxdraw.filled_polygon(self.screen, [corner1, corner2, corner3, corner4], color)

    def mouse_handler(self, pos):

        if self.program_state == "menu":
            for button_name in self.menu_buttons:
                button = self.menu_buttons[button_name]
                if button.mouse_on_button(pygame.mouse.get_pos()):
                    button.handler()

        elif self.program_state == "game":
            row, col = pos[1] // 100, pos[0] // 100

            if pos[0] < 800:
                if not self.analyzing:
                    if self.game.selected:
                        if (row, col) in self.game.selected_moves:
                            self.game.move(self.game.selected, (row, col))
                            self.game.remove_selection()
                        else:
                            self.game.remove_selection()
                    else:
                        tile = self.game.board.grid[row][col]
                        if tile and tile.color == self.game.turn:
                            self.game.set_selection((row, col))
                else:
                    pass
            else:
                for button_name in self.game_buttons:
                    button = self.game_buttons[button_name]
                    if button.mouse_on_button(pygame.mouse.get_pos()):
                        button.handler()

    def start_analysis(self):
        self.game_buttons["analyze"] = Button((1020, 20), "monospace", 30, BLACK, 3, "Stop Analysis", DARK_GREEN, GREEN, self.stop_analysis)
        self.analyzing = True
        self.game.search_best_move()

    def stop_analysis(self):
        self.game_buttons["analyze"] = Button((1020, 20), "monospace", 30, BLACK, 3, "Analyze", DARK_GREEN, GREEN, self.start_analysis)
        self.analyzing = False
        self.game.stop_search()


if __name__ == "__main__":
    G = Gui()
    G.main()
