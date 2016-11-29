
import pygame
from pygame.locals import *

class Tree(pygame.sprite.Sprite):
    def __init__(self, tile, r, x, y):
        super(Tree, self).__init__()

        self.tile = tile
        self.r = r
        
        rr = r + r
        self.image = pygame.Surface((rr, rr), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.midx = tile.rect.x + x
        self.midy = tile.rect.y + y
        self.rect.x = self.midx - r
        self.rect.y = self.midy - r
        self.r_r = (r, r)
        self.intersect_lines = [
            ((self.rect.x, self.rect.y), (self.rect.x + rr, self.rect.y + rr)),
        ]
        self.redraw = True
        self.height = 1.0 # used for vision

    def draw(self):
        if not self.redraw:
            return
        self.redraw = False
        r_r = self.r_r
        if self.tile.world.active_item is self:
            pygame.draw.circle(self.image, (0, 0, 255), r_r, self.r, 0)
        else:
            pygame.draw.circle(self.image, (0, 80, 0), r_r, self.r, 0)
        pygame.draw.circle(self.image, (0, 128, 0), r_r, self.r - 2, 0)

    def __str__(self):
        return "Tree at {},{}".format(self.rect.x, self.rect.y)

    def __repr__(self):
        return "<Tree at {},{}>".format(self.rect.x, self.rect.y)
