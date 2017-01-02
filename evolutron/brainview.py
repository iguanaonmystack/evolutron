
import pygame
from pygame.locals import *

import viewport
import group


class BrainView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(BrainView, self).__init__(
            parent, viewport_rect, viewport_rect.w, viewport_rect.h)
        self._brain = None
        self.height = viewport_rect.h
        self.font = pygame.font.Font(None, 18)
        self.active_item = None
        self.input_labels = ('const', 'vis left', 'vis right', 'water', 'grass', 'forest', 'haptic', 'energy/10k')
        self.neuron_spacing = (75, self.height // (len(self.input_labels) + 1))
        self.neuron_width = 40
        self.neuron_height = self.neuron_spacing[1] // 2

    @property
    def brain(self):
        return self._brain

    @brain.setter
    def brain(self, brain):
        self._brain = brain
        self.allneurons = group.Group()
        if brain is None:
            return
        self.active_item = None
        for i, layer in enumerate((brain.inputs, brain.hidden0, brain.outputs)):
            for j, neuron in enumerate(layer):
                centre = self.neuron_centre(i, j)
                neuron.connect_viewport(self, self.neuron_width, self.neuron_height, self.neuron_centre(i, j))
                self.allneurons.add(neuron)

    def neuron_centre(self, layer, node_index):
        return [20 + self.neuron_spacing[0] * layer,
                self.neuron_spacing[1] + self.neuron_spacing[1] * node_index]

    def draw(self):
        brain = self._brain

        self.canvas.fill((0, 0, 0))
        
        if brain is None:
            self.image.blit(self.canvas, self.drag_offset)
            return

        input_labels = self.input_labels
        hidden_labels = ()
        output_labels = ('angle ch', 'impulse', 'spawn')

        for i, layer in enumerate((input_labels, hidden_labels, output_labels)):
            for j, label in enumerate(layer):
                centrepos = self.neuron_centre(i, j)
                text = self.font.render(label, True, (255, 255, 255))
                textrect = text.get_rect()
                self.canvas.blit(text, (centrepos[0] - self.neuron_width // 2, centrepos[1] - self.neuron_height // 2 - textrect.h))

        layers = brain.inputs, brain.hidden0, brain.outputs
        for i, layer in enumerate(layers):
            for j, neuron in enumerate(layer):
                # draw axons
                for k, weight in enumerate(neuron.input_weights):
                    if self.active_item:
                        if neuron is not self.active_item \
                        and i and layers[i-1][k] is not self.active_item:
                            continue

                    val = int(min(abs(weight) * 255, 255))
                    if weight > 0:
                        colour = (0, val, val)
                    else:
                        colour = (val, 0, 0)
                    start = self.neuron_centre(i - 1, k)
                    end = self.neuron_centre(i, j)
                    pygame.draw.line(self.canvas, colour, start, end, 2)
                    if self.active_item:
                        text = self.font.render(
                            '%.2f' % weight, True, (255, 255, 255))
                        rect = text.get_rect()
                        label_pos = (
                            (start[0] + end[0]) // 2 - rect.w // 2,
                            (start[1] + end[1]) // 2 - rect.h // 2)
                        self.canvas.blit(text, label_pos)
        self.allneurons.draw(self.canvas)

        self.image.blit(self.canvas, self.drag_offset)


    def onclick(self, relpos, button):
        if button != 1:
            self.active_item = None
            return

        canvas_pos = [relpos[i] - self.drag_offset[i] for i in (0, 1)]
        clicked_neurons = [n for n in self.allneurons
                           if n.rect.collidepoint(canvas_pos)]
        if clicked_neurons:
            self.active_item = clicked_neurons[0]
            return
        self.active_item = None

