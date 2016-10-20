import random

import pygame
from pygame.locals import *

import viewport
import tiles
import characters
import group
import tree
import mapgen

MIN_CHARACTERS = 100

class WorldView(viewport.Viewport):
    def __init__(self, parent, viewport_rect, canvas_w, canvas_h):
        super(WorldView, self).__init__(parent, viewport_rect, canvas_w, canvas_h)

        self.tile_w = 50
        self.tile_h = 50
        self.map = mapgen.Map.from_random(canvas_w//self.tile_w, canvas_h//self.tile_h)

        self.alltiles = group.Group()
        self.alltiles_coords = {}

        self.alltrees = group.Group()
        self.allfood = group.Group()

        # Generate tiles and trees
        for i, row in enumerate(self.map):
            for j, tile in enumerate(row):

                block = tiles.TileView(
                    self, i, j, self.tile_w, self.tile_h, tile,
                    fertility=random.random())
                self.alltiles.add(block)
                self.alltiles_coords[i, j] = block

        self.allcharacters = group.Group()
        self.active_item = None
        self.age = 0.0

    def _create_character(self):
        character = characters.Character.from_random(self)
        while character._x is None \
        or pygame.sprite.spritecollideany(character, self.allcharacters) \
        or pygame.sprite.spritecollideany(character, self.alltrees):
            character.x = random.randint(0, self.canvas_w - character.r * 2)
            character.y = random.randint(0, self.canvas_h - character.r * 2)
        self.allcharacters.add(character)
        # debugging:
        if self.active_item is None:
            self.active_item = character
            self.parent.brainview.brain = character.brain

    def update(self):
        self.age += 1
        while len(self.allcharacters) < MIN_CHARACTERS:
            self._create_character()
        for group in (self.alltiles, self.allcharacters):
            group.update()
        self.allcharacters.collisions()

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
        for group in (self.alltiles, self.allfood, self.allcharacters, self.alltrees):
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
                if self.active_item is not None \
                and self.active_item is not clicked_sprites[0]:
                    self.active_item.redraw = True
                self.active_item = clicked_sprites[0]
                self.active_item.redraw = True
                if hasattr(self.active_item, 'brain'):
                    self.parent.brainview.brain = self.active_item.brain
                else:
                    self.parent.brainview.brain = None
                return

        self.parent.brainview.brain = None
        if self.active_item:
            self.active_item.redraw = True
            self.active_item = None


