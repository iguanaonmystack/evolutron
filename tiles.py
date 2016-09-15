import pygame
from pygame.locals import *

class Tile(pygame.sprite.Sprite):
    default_w = 100
    default_h = 100

    def __init__(self, x, y, w=default_w, h=default_h):
        pygame.sprite.Sprite.__init__(self)
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        
        self.image = pygame.Surface((self._w, self._h)).convert()
        self.image.fill((0,0,255))

        self.rect = self.image.get_rect()

        self.rect.x = self._x * self._w
        self.rect.y = self._y * self._h

    @property
    def colour(self):
        pass

    @colour.setter
    def colour(self, color):
       self.image.fill(color)

