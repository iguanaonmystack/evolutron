
import pygame
from pygame.locals import *

import viewport

class InfoPane(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(InfoPane, self).__init__(
            parent, viewport_rect, viewport_rect.w, viewport_rect.h)
        self._text = ''
        self._text_changed = True
        self.font = pygame.font.Font(None, 18)
    
    def draw(self):
        if self._text_changed:
            self.canvas.fill((255, 255, 255))
            s = self._text
            off = 0
            for line in s.split('\n'):
                text = self.font.render(line, True, (0, 0, 0))
                rect = text.get_rect()
                self.canvas.blit(text, (0, 0 + off))
                off += rect.h
            self.image.blit(self.canvas, self.drag_offset)
            self._text_changed = False

    @property
    def text(self):
        raise NotImplementedError()
    @text.setter
    def text(self, value):
        if value != self._text:
            self._text_changed = True
        self._text = value

