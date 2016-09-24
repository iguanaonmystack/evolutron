
import pygame
from pygame.locals import *

import group
import worldview
import infopane
import brainview
import popview

class Window(object):
    """Logical representation of the application window."""

    def __init__(self, screen, world_w, world_h):

        self.screen = screen
        self.onresize(1000, 1000)

        self.allsprites = group.Group()

        self.world = worldview.WorldView(
            self, Rect(200, 0, 1000 - 200, 1000), world_w, world_h)
        self.allsprites.add(self.world)

        self.infopane = infopane.InfoPane(self, Rect(0, 0, 200, 300))
        self.allsprites.add(self.infopane)

        self.brainview = brainview.BrainView(self, Rect(0, 300, 200, 400))
        self.allsprites.add(self.brainview)

        self.genesview = popview.GenePopView(self, Rect(0, 700, 200, 200))
        self.allsprites.add(self.genesview)
        self.popview = popview.TimePopView(self, Rect(0, 900, 200, 100))
        self.allsprites.add(self.popview)

    def onresize(self, window_w, window_h):
        self.background = pygame.Surface(self.screen.get_size()).convert()
        if hasattr(self, 'world'):
            self.world.resize(Rect(200, 0, window_w - 200, window_h))
            self.brainview.resize(Rect(0, 300, 200, window_h - 600))
            self.genesview.resize(Rect(0, window_h - 300, 200, 200))
            self.popview.resize(Rect(0, window_h - 100, 200, 100))

    def update(self):
        self.world.update()

    def frame(self):
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
       

