
import pygame
from pygame.locals import *

class Tree(pygame.sprite.Sprite):
    def __init__(self, tile, r, x, y):
        super(Tree, self).__init__()

        self.tile = tile
        self.r = r

        self.image = pygame.Surface(
            (self.r * 2 + 4, self.r * 2 + 4), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = tile.rect.x + x - self.r
        self.rect.y = tile.rect.y + y - self.r
        self.r_r = (r, r)
        self.redraw = True

    def draw(self):
        if not self.redraw:
            return
        self.redraw = False
        r_r = self.r_r
        pygame.draw.circle(self.image, (0, 80, 0), r_r, self.r, 0)
        pygame.draw.circle(self.image, (0, 128, 0), r_r, self.r - 2, 0)

