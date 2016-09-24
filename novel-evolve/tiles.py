import random

import pygame
from pygame.locals import *

from novel import terrains

import group
import food

class TileView(pygame.sprite.Sprite):
    def __init__(self, world, x, y, w, h, tile, fertility=1.0):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tile = tile
        self.fertility_mult = 1.0
        self.r_mult = 255
        self.g_mult = 0
        self.b_mult = 0
        if isinstance(self.tile.terrain, terrains.Meadow):
            self.fertility_mult = 0.05
            self.r_mult = 120
            self.g_mult = 180
            self.b_mult = 120
        elif isinstance(self.tile.terrain, terrains.Lake):
            self.fertility_mult = 0
            self.r_mult = 0
            self.g_mult = 0
            self.b_mult = 215
        elif isinstance(self.tile.terrain, terrains.Forest):
            self.fertility_mult = 0.1
            self.r_mult = 0
            self.g_mult = 215
            self.b_mult = 0
        else:
            print('unknown terrain type: %r' % self.tile)

        if fertility > 1.0:
            raise ValueError('fertility must be <= 1.0')
        self.fertility = fertility
        
        self.image = pygame.Surface((self.w, self.h)).convert()
        self.image.fill((0,0,255))
        self.redraw = True

        self.rect = self.image.get_rect()

        self.rect.x = self.x * self.w
        self.rect.y = self.y * self.h

        self.allfood = group.Group()
        self.max_food = 10

    def update(self, dt):
        # create some food
        if len(self.allfood) < self.max_food:
            if random.random() < (self.fertility * self.fertility_mult * dt):
                f = food.Food(
                    self, random.randint(0, self.w), random.randint(0, self.h))
                self.allfood.add(f)
                self.world.allfood.add(f)

    def draw(self):
        if not self.redraw:
            return
        self.redraw = False

        new_fill = (int(self.fertility * self.r_mult + 40),
                    int(self.fertility * self.g_mult + 40),
                    int(self.fertility * self.b_mult + 40))
        self.last_fill = new_fill
        self.image.fill(new_fill)
        if self.world.active_item is self:
            pygame.draw.lines(self.image, (0, 0, 255), 1, [
                (0, 0), (self.w - 1, 0), (self.w - 1, self.h - 1), (0, self.h - 1)
            ], 3)
            self.last_fill = None

    def __str__(self):
        return '\n'.join([
            'Tile:',
            'terrain: %s' % self.tile.terrain.__class__.__name__,
            'fertility: %s' % self.fertility,
        ])

