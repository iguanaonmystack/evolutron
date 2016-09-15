import random

import pygame
from pygame.locals import *

import tiles
import characters

class World(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.resize(1000, 1000)
        self.viewport_offset = [0, 0]
    
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
        for i in range(100):
            character = characters.Character(self)
            while character.x is None \
            or pygame.sprite.spritecollideany(character, self.allcharacters):
                character.x = random.randint(0, w - character.r * 2)
                character.y = random.randint(0, h - character.r * 2)
                character.acc_x = random.random() * 4 - 2
                character.acc_y = random.random() * 4 - 2
            self.allcharacters.add(character)

        self.active_sprite = None
    
    def update(self, dt):
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.update()

    def frame(self, tick_progress):
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.draw(self.background)
        font = pygame.font.Font(None, 18)
        self.screen.blit(self.background, self.viewport_offset)
        if self.active_sprite:
            s = str(self.active_sprite)
            off = 0
            for line in s.split('\n'):
                text = font.render(line, True, (0, 0, 0))
                rect = text.get_rect()
                image = pygame.Surface((rect.w, rect.h)).convert()
                image.fill((255, 255, 255))
                self.screen.blit(image, (0, 0 + off))
                self.screen.blit(text, (0, 0 + off))
                off += rect.h
        pygame.display.flip()


    def resize(self, viewport_w, viewport_h):
        self.viewport_size = viewport_w, viewport_h
        self.screen = pygame.display.set_mode(self.viewport_size, RESIZABLE)

        # We shouldn't actually see the background, but have a nice grey for it.
        background = pygame.Surface((self.w, self.h))
        background = background.convert()
        background.fill((128,128,128))
        self.background = background

 
    def drag(self, rel):
        size = self.w, self.h
        for i in (0, 1):
            self.viewport_offset[i] = self.viewport_offset[i] + rel[i]
            if self.viewport_offset[i] > 0:
                self.viewport_offset[i] = 0
            if self.viewport_offset[i] < - size[i] + self.viewport_size[i]:
                self.viewport_offset[i] = - size[i] + self.viewport_size[i];


    def click(self, pos):
        clicked_sprites = [s for s in self.allcharacters if s.rect.collidepoint(pos)]
        if clicked_sprites:
            self.active_sprite = clicked_sprites[0]
        else:
            self.active_sprite = None
