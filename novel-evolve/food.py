
import pygame
from pygame.locals import *

class Food(pygame.sprite.Sprite):
    def __init__(self, tile, x, y):
        super(Food, self).__init__()

        self.tile = tile
        self.energy = 1000

        self.image = pygame.Surface((9, 5), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = tile.rect.x + x
        self.rect.y = tile.rect.y + y
        self.redraw = True

    def eaten(self):
        self.tile.allfood.remove(self)
        self.tile.world.allfood.remove(self)

    def draw(self):
        if self.redraw:
            pygame.draw.ellipse(self.image, (96, 96, 0), Rect(3, 2, 3, 3), 0)
            pygame.draw.ellipse(self.image, (128, 128, 0), Rect(0, 0, 9, 5), 0)
            self.redraw = False

