import sys
import pygame
from pygame.locals import *
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


WIDTH = 800
HEIGHT = 800

class Gui(object):
    """
    Main game class, where the main game function exists and includes other game functionalities.
    """

    def __init__(self):

        pygame.init()
        self.clock = pygame.time.Clock()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        
        # There are program states
        # menu, game,
        #
        self.program_state = "menu"

        # Define all buttons that are going to be used
        # Inside the program, using a dictionary.
        # Format {
        #   button_name: button_object
        # }

        
        self.buttons = {
            # Button class (program_state, pos, text_font, text_color, text_padding, message, color, hover_color, handler)
            "newgame": Button("menu", (200, 400), "monospace", 30, BLACK, 3, "NEW GAME", DARK_GREEN, GREEN, self.new_game),
            "exit":    Button("menu", (200, 600), "monospace", 30, BLACK, 3, "QUIT", DARK_RED, RED, self.quit)
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
                    sys.exit()

                # event button 1 is the left mouse button.
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.mouse_handler(pygame.mouse.get_pos())

            self.draw_gui()

    def new_game(self):

        self.game = internals.Game()
        self.program_state = "game"
        

    def quit(self):
        pygame.quit()  # quits pygame
        sys.exit()

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

    def draw_buttons(self):
        for button_name in self.buttons:
            button = self.buttons[button_name]
            if button.program_state == self.program_state:
                button.draw(self.screen, pygame.mouse.get_pos())

    def draw_text(self, pos, size, color, message):
        """
        Method that draws a text to the screen
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
            for button_name in self.buttons:
                button = self.buttons[button_name]
                if button.mouse_on_button(pygame.mouse.get_pos()):
                    button.handler()

        elif self.program_state == "game":
            row, col = pos[1] / 100, pos[0] / 100
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

if __name__ == "__main__":
    G = Gui()
    G.main()