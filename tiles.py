import pygame
from pygame.locals import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, world, x, y, w, h, max_nutrition=255):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
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
        self.last_fill = (0,0,255)

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
        self._nutrition += 25 * dt
        if self._nutrition > self._max_nutrition:
            self._nutrition = self._max_nutrition
        
    def draw(self):
        new_fill = (int(self._nutrition), 0, 0)
        if new_fill != self.last_fill:
            self.last_fill = new_fill
            self.image.fill(new_fill)
        if self.world.active_item is self:
            pygame.draw.lines(self.image, (0, 0, 255), 1, [
                (0, 0), (self._w - 1, 0), (self._w - 1, self._h - 1), (0, self._h - 1)
            ], 3)
            self.last_fill = None

    def __str__(self):
        return '\n'.join([
            'Tile:',
            'nutrition: %s' % self._nutrition,
            'max_nutrition: %s' % self._max_nutrition,
        ])

