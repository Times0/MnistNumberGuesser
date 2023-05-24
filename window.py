import sys

import PygameUIKit.button as button
import pygame.sprite
import torch
from PygameUIKit import Group
from PygameUIKit.label import Label

from constants import *

SIZE_PIXEL = 18


class Window:
    def __init__(self, win):
        self.game_is_on = True
        self.win = win
        font = pygame.font.SysFont("Montserrat", 30)
        self.clear_btn = button.ButtonText(RED, self.clear, "CLEAR", border_radius=5, font_color=WHITE, font=font)
        # self.guess_btn = button.ButtonText(BLUE, self.calculate_and_show_prediction, "GUESS", border_radius=5, font_color=WHITE,
        #                                    font=font)

        self.label = Label("Predictions :", font_color=WHITE, font=font)
        self.predictions_labels = []
        for i in range(10):
            text = f"{i} : 0.0"
            self.predictions_labels.append(Label(text, font_color=WHITE, font=font))
        self.prediction_values = [0.1] * 10

        self.objs = Group(self.clear_btn)
        self.grid = Grid(28)

        import os
        # current dir
        sys.path.append(r"C:\Programmation\Python\Cool Projects\mnist_gui")
        self.model = torch.load("model_good.pt")

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            clock.tick(FPS)
            self.win.fill((40, 44, 52))
            self.events()
            self.draw(self.win)

    def events(self):
        events = pygame.event.get()
        self.objs.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.game_is_on = False

        if pygame.mouse.get_pressed()[0]:
            pos = pygame.mouse.get_pos()
            W, H = self.win.get_size()
            x_grid = W / 2 - SIZE_PIXEL * self.grid.n / 2 - 100
            y_grid = H / 2 - SIZE_PIXEL * self.grid.n / 2
            self.grid.handle_event(pos, x_grid, y_grid)
            self.calculate_and_show_prediction()

    def draw(self, win):
        W, H = win.get_size()
        x_grid = W / 2 - SIZE_PIXEL * self.grid.n / 2 - 100
        y_grid = H / 2 - SIZE_PIXEL * self.grid.n / 2

        self.grid.draw(win, x_grid, y_grid, draw_lines=False)
        self.clear_btn.draw(win, x_grid - self.clear_btn.rect.width - 10, y_grid + 10)

        self.label.draw(win, W - 300, y_grid + 50)
        for i in range(len(self.predictions_labels)):
            self.predictions_labels[i].draw(win, W - 300, y_grid + 50 + (i + 1) * 30)

        pygame.display.flip()

    def update_labels(self):
        max_pred = max(self.prediction_values)
        for i in range(len(self.prediction_values)):
            self.predictions_labels[i].text = f"{i} : {self.prediction_values[i]:.3f}"
            if self.prediction_values[i] == max_pred and max_pred > 0.5:
                self.predictions_labels[i].font_color = RED
            else:
                self.predictions_labels[i].font_color = WHITE
            self.predictions_labels[i].render_new_text()

    def clear(self):
        self.grid = Grid(28)
        self.prediction_values = [0] * len(self.prediction_values)
        self.update_labels()

    def create_torch_image(self) -> torch.Tensor:
        img = torch.zeros((1, 1, 28, 28))
        for i in range(28):
            for j in range(28):
                img[0][0][i][j] = self.grid.tab[j][i]
        # show the image
        return img

    def compute_prediction_values(self):
        img = self.create_torch_image()
        output = self.model(img)
        return output

    def calculate_and_show_prediction(self):
        vals = self.compute_prediction_values()
        self.prediction_values = vals[0].tolist()
        self.update_labels()


class Grid:
    def __init__(self, n):
        self.tab = [[0 for i in range(n)] for j in range(n)]
        self.n = n

    def draw(self, win, x_offset, y_offset, draw_lines=True):
        w, h = SIZE_PIXEL, SIZE_PIXEL

        for i in range(self.n):
            for j in range(self.n):
                x = i * w
                y = j * h
                if self.tab[i][j] == 0:
                    pygame.draw.rect(win, WHITE, (x + x_offset, y + y_offset, w, h))
                else:
                    pygame.draw.rect(win, BLACK, (x + x_offset, y + y_offset, w, h))
        if draw_lines:
            # draw horizontal lines
            for i in range(self.n + 1):
                pygame.draw.line(win, LIGHTBLACK, (x_offset, i * h + y_offset),
                                 (self.n * w + x_offset, i * h + y_offset))
            # draw vertical lines
            for i in range(self.n + 1):
                pygame.draw.line(win, LIGHTBLACK, (i * w + x_offset, y_offset),
                                 (i * w + x_offset, self.n * h + y_offset))

    def handle_event(self, pos, x_offset, y_offset):
        w, h = SIZE_PIXEL, SIZE_PIXEL

        x, y = pos
        x -= x_offset
        y -= y_offset

        i = x // w
        j = y // h
        if 0 <= i < self.n and 0 <= j < self.n:
            i, j = int(i), int(j)
            self.tab[i][j] = 1
