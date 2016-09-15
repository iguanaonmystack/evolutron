import random

import pygame
from pygame.locals import *

import tiles
import characters

class World(object):
    def __init__(self, w, h, background):
        self.w = w
        self.h = h
        self.background = background

        self.alltiles = pygame.sprite.Group()
        for i in range(self.w // tiles.Tile.default_w):
            for j in range(self.h // tiles.Tile.default_h):
                block = tiles.Tile(i, j)
                block.colour = (random.randint(0, 255), 0, 0)
                self.alltiles.add(block)

        self.allwalls = pygame.sprite.Group()
        self.allwalls.add(tiles.Tile(0, -1, self.w, 100))
        self.allwalls.add(tiles.Tile(self.w / 100, 0, 100, self.h))
        self.allwalls.add(tiles.Tile(0, self.h / 100, self.w, 100))
        self.allwalls.add(tiles.Tile(-1, 0, 100, self.h))
        
        self.allcharacters = pygame.sprite.Group()
        for i in range(10):
            character = characters.Character(self)
            while character.x is None \
            or pygame.sprite.spritecollideany(character, self.allcharacters):
                character.x = random.randint(0, w - character.r * 2)
                character.y = random.randint(0, h - character.r * 2)
                character.acc_x = random.random() * 4 - 2
                character.acc_y = random.random() * 4 - 2
            self.allcharacters.add(character)
    
    def update(self):
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.update()
            group.draw(self.background)

