import random

import pygame
from pygame.locals import *

import viewport
import tiles
import characters
import group

MIN_CHARACTERS = 100

class WorldView(viewport.Viewport):
    def __init__(self, parent, viewport_rect, canvas_w, canvas_h):
        super(WorldView, self).__init__(parent, viewport_rect, canvas_w, canvas_h)

        self.tile_w = 100
        self.tile_h = 100
        self.alltiles = group.Group()
        self.alltiles_coords = {}
        for i in range(self.canvas_w // self.tile_w):
            for j in range(self.canvas_h // self.tile_h):
                block = tiles.Tile(self, i, j, self.tile_w, self.tile_h,
                                   max_nutrition=random.randint(0, 255))
                self.alltiles.add(block)
                self.alltiles_coords[i, j] = block

        self.allwalls = group.Group()
        self.allwalls.add(
            tiles.Tile(self, 0, -1, self.canvas_w, 100))
        self.allwalls.add(
            tiles.Tile(self, self.canvas_w / 100, 0, 100, self.canvas_h))
        self.allwalls.add(
            tiles.Tile(self, 0, self.canvas_h / 100, self.canvas_w, 100))
        self.allwalls.add(
            tiles.Tile(self, -1, 0, 100, self.canvas_h))
        
        self.allcharacters = group.Group()
        self.active_item = None
        self.age = 0.0

    def _create_character(self):
        character = characters.Character.from_random(self)
        while character._x is None \
        or pygame.sprite.spritecollideany(character, self.allcharacters):
            character.x = random.randint(0, self.canvas_w - character.r * 2)
            character.y = random.randint(0, self.canvas_h - character.r * 2)
        self.allcharacters.add(character)
        # debugging:
        if self.active_item is None:
            self.active_item = character
            self.parent.brainview.brain = character.brain

    def update(self, dt):
        self.age += dt
        while len(self.allcharacters) < MIN_CHARACTERS:
            self._create_character()
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.update(dt)

    def jump_to(self, item):
        x = item.rect.x - self.rect.w // 2
        y = item.rect.y - self.rect.h // 2
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > self.canvas_w - self.rect.w:
            x = self.canvas_w - self.rect.w
        if y > self.canvas_h - self.rect.h:
            y = self.canvas_h - self.rect.h
        self.drag_offset[0] = -x
        self.drag_offset[1] = -y

    def draw(self):
        for group in (self.alltiles, self.allwalls, self.allcharacters):
            group.draw(self.canvas)

        if self.active_item:
            self.parent.infopane.text = str(self.active_item)
        else:
            self.parent.infopane.text = ''

        self.image.blit(self.canvas, self.drag_offset)

    def onclick(self, relpos, button):
        if button == 1:
            canvas_pos = [relpos[i] - self.drag_offset[i] for i in (0, 1)]
            clicked_sprites = []
            if not clicked_sprites:
                clicked_sprites = [s for s in self.allcharacters
                                   if s.rect.collidepoint(canvas_pos)]
            if not clicked_sprites:
                clicked_sprites = [s for s in self.alltiles
                                   if s.rect.collidepoint(canvas_pos)]

            if clicked_sprites:
                self.active_item = clicked_sprites[0]
                if hasattr(self.active_item, '_genome'):
                    self.parent.brainview.brain = self.active_item.brain
                else:
                    self.parent.brainview.brain = None
                return
            
        self.parent.brainview.brain = None
        self.active_item = None
 
