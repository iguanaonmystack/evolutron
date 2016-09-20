

import pygame
from pygame.locals import *

import group
import world
import infopane

class Window(object):
    """Logical representation of the application window."""

    def __init__(self, world_w, world_h):

        self.onresize(1000, 1000)

        self.allsprites = group.Group()

        self.world = world.World(
            self, Rect(200, 0, 1000 - 200, 1000), world_w, world_h)
        self.allsprites.add(self.world)

        self.infopane = infopane.InfoPane(self, Rect(0, 0, 200, 500))
        self.allsprites.add(self.infopane)

    def onresize(self, window_w, window_h):
        self.window_size = window_w, window_h
        self.screen = pygame.display.set_mode(self.window_size, RESIZABLE)

        self.background = pygame.Surface(self.window_size).convert()
        if hasattr(self, 'world'):
            self.world.resize(Rect(200, 0, window_w - 200, window_h))

    def update(self, dt):
        self.world.update(dt)

    def frame(self, tick_progress):
        self.background.fill((128,128,128))
        self.allsprites.draw(self.background)
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()

    def ondrag(self, origin, rel):
        # rel: usually (0, 0) (-1, 0), (0, 1), etc
        clicked_sprites = [s for s in self.allsprites if s.rect.collidepoint(origin)]
        for sprite in clicked_sprites:
            # probably just one
            if hasattr(sprite, 'ondrag'):
                sprite.ondrag(rel)

    def onclick(self, screenpos, button):
        # button: 1/2/3=left/middle/right, 4/5=wheel
        clicked_sprites = [s for s in self.allsprites if s.rect.collidepoint(screenpos)]
        for sprite in clicked_sprites:
            if hasattr(sprite, 'onclick'):
                relpos = (screenpos[0] - sprite.rect.x, screenpos[1] - sprite.rect.y)
                sprite.onclick(relpos, button)
       

