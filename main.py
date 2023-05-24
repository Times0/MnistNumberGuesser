import pygame

from constants import *
from window import Window

if __name__ == "__main__":
    pygame.init()
    pygame.display.set_caption("Game")
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Window(win)
    game.run()
