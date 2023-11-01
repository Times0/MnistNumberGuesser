import math
from pprint import pprint

import PygameUIKit.button as button
import pygame.sprite
import torch
from PygameUIKit import Group
from PygameUIKit.label import Label
from PygameUIKit.barchart import BarChart
from pygame import Color

from constants import *

SIZE_PIXEL = 18

RED = (255, 0, 0)
WHITE = (255, 255, 255)
LIGHT_BLACK = (40, 44, 52)
BLACK = (0, 0, 0)


class Window:
    def __init__(self, win):
        self.WIDTH, self.HEIGHT = WIDTH, HEIGHT
        self.game_is_on = True
        self.win = win
        font = pygame.font.SysFont("Montserrat", 30)

        self.prediction_values = [0.1] * 10
        self.certainty_values = [0] * 10

        self.ui_group = Group()
        self.clear_btn = button.ButtonText("CLEAR", self.clear, RED, border_radius=5, font_color=Color("white"),
                                           font=font, ui_group=self.ui_group)

        labels = [str(i) for i in range(10)]
        certainty = [0] * 10
        self.bar_chart = BarChart(certainty, labels=labels, ui_group=self.ui_group, max_value=100,
                                  labels_color=Color("white"))

        self.label = Label("Predictions :", font_color=WHITE, font=font)
        self.predictions_labels = []
        for i in range(10):
            text = f"{i} : 0.0"
            self.predictions_labels.append(Label(text, font_color=WHITE, font=font))

        self.grid = Grid(28)

        self.writing = False

        # Model
        self.model = torch.load("model_good.pt")

    def run(self):
        clock = pygame.time.Clock()
        while self.game_is_on:
            dt = clock.tick(FPS) / 1000
            self.win.fill((40, 44, 52))
            self.events()
            self.update(dt)
            self.draw(self.win)

    def events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.game_is_on = False
            self.ui_group.handle_event(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.writing = True

            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.writing = False
                    self.calculate_and_show_prediction()

            if event.type == pygame.MOUSEMOTION:
                if self.writing:
                    pos = pygame.mouse.get_pos()
                    x, y = self.grid.rect.topleft
                    self.grid.handle_event(pos, x, y)
                self.calculate_and_show_prediction()

            if event.type == pygame.WINDOWRESIZED:
                self.WIDTH, self.HEIGHT = self.win.get_size()

        # if pygame.mouse.get_pressed()[0]:
        #     pos = pygame.mouse.get_pos()
        #     W, H = self.win.get_size()
        #     x_grid = W / 2 - SIZE_PIXEL * self.grid.n / 2 - 100
        #     y_grid = H / 2 - SIZE_PIXEL * self.grid.n / 2
        #     self.grid.handle_event(pos, x_grid, y_grid)

    def update(self, dt):
        self.ui_group.update(dt)

    def draw(self, win):
        W, H = self.WIDTH, self.HEIGHT
        w_grid = SIZE_PIXEL * self.grid.n
        h_grid = SIZE_PIXEL * self.grid.n
        x_grid = W / 2 - w_grid / 2
        y_grid = (H / 2 - h_grid / 2) * 0.5

        self.grid.draw(win, x_grid, y_grid, draw_lines=False)
        self.clear_btn.draw(win, x_grid - self.clear_btn.rect.width - 50, y_grid + 10)

        # draw the bar chart
        self.bar_chart.draw(win, x_grid, y_grid + h_grid + 10, w_grid, H - y_grid - h_grid - 50)
        pygame.display.flip()

    def update_labels(self):
        pprint(self.prediction_values)
        max_value = math.exp(max(self.prediction_values))

        for i, value in enumerate(self.prediction_values):
            self.bar_chart.change_value(i, math.exp(value) * 100 / max_value)

        pprint(self.certainty_values)

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
        self.model.eval()
        output = self.model(img)
        return output

    def calculate_and_show_prediction(self):
        self.prediction_values = self.compute_prediction_values()[0].tolist()
        self.update_labels()


class Grid:
    def __init__(self, n):
        self.tab = [[0 for i in range(n)] for j in range(n)]
        self.n = n
        self.rect = pygame.Rect(0, 0, 0, 0)

    def draw(self, win, x_offset, y_offset, draw_lines=True):
        w, h = SIZE_PIXEL, SIZE_PIXEL
        self.rect = pygame.Rect(x_offset, y_offset, w * self.n, h * self.n)
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
                pygame.draw.line(win, LIGHT_BLACK, (x_offset, i * h + y_offset),
                                 (self.n * w + x_offset, i * h + y_offset))
            # draw vertical lines
            for i in range(self.n + 1):
                pygame.draw.line(win, LIGHT_BLACK, (i * w + x_offset, y_offset),
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
            for k in range(i - 1, i + 2):
                for l in range(j - 1, j + 2):
                    if 0 <= k < self.n and 0 <= l < self.n:
                        self.tab[k][l] = 1
