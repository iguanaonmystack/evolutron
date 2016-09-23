import pygame
from pygame.locals import *

from novel import terrains

class TileView(pygame.sprite.Sprite):
    def __init__(self, world, x, y, w, h, tile, fertility=1.0):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self._x = x
        self._y = y
        self._w = w
        self._h = h
        self.tile = tile
        self.r_mult = 255
        self.g_mult = 0
        self.b_mult = 0
        if isinstance(self.tile.terrain, terrains.Meadow):
            self.r_mult = 120
            self.g_mult = 180
            self.b_mult = 120
        elif isinstance(self.tile.terrain, terrains.Lake):
            self.r_mult = 0
            self.g_mult = 0
            self.b_mult = 215
        elif isinstance(self.tile.terrain, terrains.Forest):
            self.r_mult = 0
            self.g_mult = 215
            self.b_mult = 0
        else:
            print('unknown terrain type: %r' % self.tile)

        if fertility > 1.0:
            raise ValueError('fertility must be <= 1.0')
        self.fertility = fertility
        
        self.image = pygame.Surface((self._w, self._h)).convert()
        self.image.fill((0,0,255))
        self.last_fill = (0,0,255)

        self.rect = self.image.get_rect()

        self.rect.x = self._x * self._w
        self.rect.y = self._y * self._h

    def update(self, dt):
        pass
        
    def draw(self):

        new_fill = (int(self.fertility * self.r_mult + 40),
                    int(self.fertility * self.g_mult + 40),
                    int(self.fertility * self.b_mult + 40))
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
            'terrain: %s' % self.tile.terrain.__class__.__name__,
            'fertility: %s' % self.fertility,
        ])

