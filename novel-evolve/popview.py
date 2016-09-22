import operator

import pygame
from pygame.locals import *

import viewport
import characters

class GenePopView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(GenePopView, self).__init__(
            parent, viewport_rect, viewport_rect.w, 100)
        self.font = pygame.font.Font(None, 18)
        self.xwidth = 2
        self.ywidth = 2
        self.sorted_chars = []

    def draw(self):
        self.canvas.fill((0, 0, 0))
        off = 0
        self.sorted_chars = sorted(
            self.parent.world.allcharacters,
            key=operator.attrgetter('_created'))
        xwidth = self.xwidth
        ywidth = self.ywidth
        for character in self.sorted_chars:
            g = character._genome
            s = selected = (self.parent.world.active_item is character) * 255
            xoff = 0

            colour = int(g.radius / 30. * 255)
            start = (xoff, off)
            xoff += xwidth
            end = (xoff, off)
            pygame.draw.line(self.canvas, (colour, colour, s or colour),
                             start, end, ywidth)

            colour = int(g.hidden_neurons / 10. * 255)
            start = (xoff, off)
            xoff += xwidth
            end = (xoff, off)
            pygame.draw.line(self.canvas, (colour, colour, s or colour),
                                           start, end, ywidth)

            # This style should show two creatures 'matching up' even if one
            # of them had their whole length of genome changed by a mutated
            # hidden_neurons gene.
            for i in range(g.hidden_neurons):
                for j in range(g._inputs):
                    weight = g.hidden0_weights[i * g._inputs + j]             
                    colour = int(characters.sigmoid(weight) * 255)
                    start = (xoff, off)
                    xoff += xwidth
                    end = (xoff, off)
                    pygame.draw.line(
                        self.canvas, (colour, colour, s or colour),
                        start, end, ywidth)
                for j in range(g._outputs):
                    weight = g.hidden0_weights[i * g._outputs + j]             
                    colour = int(characters.sigmoid(weight) * 255)
                    start = (xoff, off)
                    xoff += xwidth
                    end = (xoff, off)
                    pygame.draw.line(
                        self.canvas, (colour, colour, s or colour),
                        start, end, ywidth)

            off += ywidth
            if off > 100:
                break

        self.image.blit(self.canvas, self.drag_offset)

    def onclick(self, relpos, button):
        print relpos[1], self.ywidth,
        sorted_chars_idx = relpos[1] // self.ywidth
        print sorted_chars_idx
        if sorted_chars_idx < len(self.sorted_chars):
            self.parent.world.active_item = self.sorted_chars[sorted_chars_idx]

class TimePopView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(TimePopView, self).__init__(
            parent, viewport_rect, viewport_rect.w, 100)
        self._text = ''
        self._text_changed = True
        self.font = pygame.font.Font(None, 18)
    
    def draw(self):
        if self._text_changed:
            self.canvas.fill((255, 255, 255))
            s = str(self._text)
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

class AgePopView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(AgePopView, self).__init__(
            parent, viewport_rect, viewport_rect.w, 100)
        self._text = ''
        self._text_changed = True
        self.font = pygame.font.Font(None, 18)
    
    def draw(self):
        if self._text_changed:
            self.canvas.fill((255, 255, 255))
            s = str(self._text)
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

