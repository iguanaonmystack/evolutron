import pygame
from pygame.locals import *

class Tile(pygame.sprite.Sprite):
    default_w = 100
    default_h = 100

    def __init__(self, x, y, w=default_w, h=default_h, max_nutrition=255):
        pygame.sprite.Sprite.__init__(self)
        self._x = x
        self._y = y
        self._w = w
        self._h = h

        if max_nutrition > 255:
            raise ValueError('max_nutrition must be <= 255')
        self._nutrition = max_nutrition
        self._max_nutrition = max_nutrition
        
        self.image = pygame.Surface((self._w, self._h)).convert()
        self.image.fill((0,0,255))

        self.rect = self.image.get_rect()

        self.rect.x = self._x * self._w
        self.rect.y = self._y * self._h

    @property
    def nutrition(self):
        return self._nutrition
    @nutrition.setter
    def nutrition(self, value):
        self._nutrition = value
    
    def update(self, dt):
        self._nutrition += 50
        if self._nutrition > self._max_nutrition:
            self._nutrition = self._max_nutrition
        
        if self._max_nutrition == 0:
            self.image.fill((0, 0, 0))
            return
        self.image.fill((int(self._nutrition), 0, 0))

    def __str__(self):
        return '\n'.join([
            'Tile:',
            'nutrition: %s' % self._nutrition,
            'max_nutrition: %s' % self._max_nutrition,
        ])

