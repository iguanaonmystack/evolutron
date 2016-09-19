import random

import pygame
from pygame.locals import *

import tiles
import characters
import genome
import group

MIN_CHARACTERS = 100

class World(object):
    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.resize(1000, 1000)
        self.viewport_offset = [0, 0]

        self.tile_w = 100
        self.tile_h = 100
        self.alltiles = group.Group()
        self.alltiles_coords = {}
        for i in range(self.w // self.tile_w):
            for j in range(self.h // self.tile_h):
                block = tiles.Tile(self, i, j, self.tile_w, self.tile_h,
                                   max_nutrition=random.randint(0, 255))
                self.alltiles.add(block)
                self.alltiles_coords[i, j] = block

        self.allwalls = group.Group()
        self.allwalls.add(tiles.Tile(self, 0, -1, self.w, 100))
        self.allwalls.add(tiles.Tile(self, self.w / 100, 0, 100, self.h))
        self.allwalls.add(tiles.Tile(self, 0, self.h / 100, self.w, 100))
        self.allwalls.add(tiles.Tile(self, -1, 0, 100, self.h))
        
        self.allcharacters = group.Group()
        self.active_item = None

    def _create_character(self):
        g = genome.Genome.from_random()
        character = characters.Character.from_genome(self, g)
        print "creating character"
        while character._x is None \
        or pygame.sprite.spritecollideany(character, self.allcharacters):
            character.x = random.randint(0, self.w - character.r * 2)
            character.y = random.randint(0, self.h - character.r * 2)
        self.allcharacters.add(character)

    def update(self, dt):
        print dt
        while len(self.allcharacters) < MIN_CHARACTERS:
            self._create_character()
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.update(dt)

    def frame(self, tick_progress):
        print 'frame', tick_progress
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.draw(self.background)
        self.screen.blit(self.background, self.viewport_offset)
        font = pygame.font.Font(None, 18)
        if self.active_item:
            s = str(self.active_item)
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
            self.active_item = clicked_sprites[0]
            return
        
        clicked_tiles = [t for t in self.alltiles if t.rect.collidepoint(pos)]
        if clicked_tiles:
            self.active_item = clicked_tiles[0]
            return
        
        self.active_item = None


