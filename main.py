import pygame

from constants import *
from window import Window

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Number Guesser")

    win = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    game = Window(win)
    game.run()
