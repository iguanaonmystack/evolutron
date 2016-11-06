
import pygame
from pygame.locals import *

class Tree(pygame.sprite.Sprite):
    def __init__(self, tile, r, x, y):
        super(Tree, self).__init__()

        self.tile = tile
        self.r = r
        
        rr = r + r
        self.image = pygame.Surface((rr + 4, rr + 4), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = tile.rect.x + x - r
        self.rect.y = tile.rect.y + y - r
        self.r_r = (r, r)
        self.intersect_lines = [
            ((self.rect.x, self.rect.y), (self.rect.x + rr, self.rect.y + rr)),
        ]
        self.redraw = True

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
