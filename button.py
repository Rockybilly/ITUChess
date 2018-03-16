"""
The module with the button class that is used in the game.
"""

import pygame
from pygame.locals import *
from pygame import gfxdraw

class Button(object):
    """
    The button class, this includes the buttons functionality,
    it's size, position and color. Also the method to draw the
    button.
    """

    def __init__(self, pos, text_font, font_size, text_color, text_padding, message, color, hover_color, handler, *args):

        
        self.pos = pos # The top left corner of the rectangle

        # Assign text position using the padding size given.
        self.text_pos = pos[0] + text_padding, pos[1] + text_padding

        self.text_font = pygame.font.SysFont(text_font, font_size)
        width, height = self.text_font.size(message)

        self.text_color = text_color
        self.width = width + 2 * text_padding
        self.height = height + 2 * text_padding
        self.message = message
        self.color = color
        self.hover_color = hover_color
        self.handler = handler

        # The arguments required to call the handler function 
        self.args = args 

    def draw(self, surface, mouse_pos):
        """
        Method that draws the button to the canvas.
        """

        corner1 = self.pos
        corner2 = self.pos[0] + self.width, self.pos[1]
        corner3 = self.pos[0] + self.width, self.pos[1] + self.height
        corner4 = self.pos[0], self.pos[1] + self.height

        # If mouse hovers over the button, change color.
        if self.mouse_on_button(mouse_pos):
            pygame.gfxdraw.filled_polygon(surface, [corner1, corner2, corner3, corner4], self.hover_color)
        else:
            pygame.gfxdraw.filled_polygon(surface, [corner1, corner2, corner3, corner4], self.color)

        # Draw the text
        surface.blit(self.text_font.render(self.message, 0, self.text_color), self.text_pos)

    def mouse_on_button(self, mouse_pos):
        """
        Function that returns True if the mouse is on the button.
        """

        # Compare the mouse's position with to the edges of the button
        if self.pos[0] <= mouse_pos[0] <= self.pos[0] + self.width and self.pos[1] <= mouse_pos[1] <= self.pos[1] + self.height:
            return True
        else:
            return False
