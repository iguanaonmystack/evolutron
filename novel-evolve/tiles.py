import random

import pygame
from pygame.locals import *

import group
import food
import tree

class TileView(pygame.sprite.Sprite):
    def __init__(self, world, x, y, w, h, tile):
        pygame.sprite.Sprite.__init__(self)
        self.world = world
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.tile = tile
        self.max_food = 10
        self.fertility_mult = 0.5
        self.colour = (255, 0, 0)
        if self.tile.terrain == 'meadow':
            self.fertility_mult = 0.0025
            self.colour = (80, 180, 80)
            self.max_food = 5
        elif self.tile.terrain == 'lake':
            self.fertility_mult = 0
            self.colour = (0, 0, 215)
            self.max_food = 0
        elif self.tile.terrain == 'forest':
            self.fertility_mult = 0.005
            self.colour = (0, 120, 0)
            self.max_food = 10
        else:
            print('unknown terrain type: %r' % self.tile)

        self.image = pygame.Surface((self.w, self.h)).convert()
        self.image.fill((0,0,255))
        self.redraw = True

        self.rect = self.image.get_rect()

        self.rect.x = self.x * self.w
        self.rect.y = self.y * self.h

        self.alltrees = group.Group()
        self.allfood = group.Group()

        if tile.terrain == 'forest':
            t = tree.Tree(
                self,
                random.randint(4, 18), # radius
                random.randint(0, w), # x
                random.randint(0, h)) # y
            self.alltrees.add(t)
            world.alltrees.add(t)


    def update(self):
        # create some food
        if len(self.allfood) < self.max_food:
            if random.random() < self.fertility_mult:
                f = food.Food(
                    self, random.randint(0, self.w), random.randint(0, self.h))
                self.allfood.add(f)
                self.world.allfood.add(f)

    def draw(self):
        if not self.redraw:
            return
        self.redraw = False

        self.image.fill(self.colour)
        if self.world.active_item is self:
            pygame.draw.lines(self.image, (0, 0, 255), 1, [
                (0, 0), (self.w - 1, 0), (self.w - 1, self.h - 1), (0, self.h - 1)
            ], 3)
            self.last_fill = None

    def __str__(self):
        return '\n'.join([
            'Tile:',
            'terrain: %s' % self.tile.terrain,
        ])

