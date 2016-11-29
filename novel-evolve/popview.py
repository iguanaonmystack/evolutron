import operator
import collections

import pygame
from pygame.locals import *

import viewport
import characters
import neuron

class GenePopView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(GenePopView, self).__init__(
            parent, viewport_rect, viewport_rect.w, 200)
        self.font = pygame.font.Font(None, 18)
        self.xwidth = 2
        self.ywidth = 1
        self.sorted_chars = []

    def draw(self):
        self.canvas.fill((0, 0, 0))
        off = 0
        self.sorted_chars = sorted(
            self.parent.world.allcharacters,
            key=operator.attrgetter('created'))
        xwidth = self.xwidth
        ywidth = self.ywidth
        for character in self.sorted_chars:
            g = character.genome
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
                    colour = int(neuron.sigmoid(weight) * 255)
                    start = (xoff, off)
                    xoff += xwidth
                    end = (xoff, off)
                    pygame.draw.line(
                        self.canvas, (colour, colour, s or colour),
                        start, end, ywidth)
                for j in range(g._outputs):
                    weight = g.hidden0_weights[i * g._outputs + j]             
                    colour = int(neuron.sigmoid(weight) * 255)
                    start = (xoff, off)
                    xoff += xwidth
                    end = (xoff, off)
                    pygame.draw.line(
                        self.canvas, (colour, colour, s or colour),
                        start, end, ywidth)

            off += ywidth
            if off > 200:
                break

        self.image.blit(self.canvas, self.drag_offset)

    def onclick(self, relpos, button):
        sorted_chars_idx = relpos[1] // self.ywidth
        if sorted_chars_idx < len(self.sorted_chars):
            char = self.sorted_chars[sorted_chars_idx]
            self.parent.world.active_item = char
            self.parent.brainview.brain = char.brain
            self.parent.world.jump_to(char)

class TimePopView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(TimePopView, self).__init__(
            parent, viewport_rect, viewport_rect.w, viewport_rect.h)
        self.font = pygame.font.Font(None, 18)
        self.h = viewport_rect.h
        self.pop_plots = collections.deque()
        self.avgage_plots = collections.deque()
        self.avggen_plots = collections.deque()
        self.plot_every = 5
        self.plot_count = 0

    def draw(self):
        if self.plot_count == 0:
            self.canvas.fill((0, 0, 0))
            pop = len(self.parent.world.allcharacters)
            avgage = sum(c.age for c in self.parent.world.allcharacters) / float(pop or 1)
            avggen = sum(c.gen for c in self.parent.world.allcharacters) / float(pop or 1)
            label_xoff = 0
            for label, plots, latest, colour in (
                ('Pop', self.pop_plots, pop, (255, 255, 0)),
                ('AvAge', self.avgage_plots, avgage, (0, 255, 0)),
                ('AvGen', self.avggen_plots, avggen, (0, 255, 255))):
                plots.append(latest)
                if len(plots) > 150:
                    plots.popleft()
                width = 2
                max_ = max(plots) or 1
                for i, plot in enumerate(plots):
                    x = width * i
                    y = self.h - float(plot) / max_ * (self.h - 20)
                    start = (x, y)
                    end = (x, y + 2)
                    pygame.draw.line(self.canvas, colour, start, end, width)
                text = self.font.render('%s:%d'%(label, latest), False, colour)
                rect = text.get_rect()
                self.canvas.blit(text, (label_xoff, 0))
                label_xoff += rect.w + 3
            self.image.blit(self.canvas, self.drag_offset)
        self.plot_count = (self.plot_count + 1) % self.plot_every

    @property
    def text(self):
        raise NotImplementedError()
    @text.setter
    def text(self, value):
        if value != self._text:
            self._text_changed = True
        self._text = value

