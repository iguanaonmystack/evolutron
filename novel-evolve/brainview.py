
import pygame
from pygame.locals import *

import viewport
import group

def neuron_centre(layer, node_index):
    return [20 + 75 * layer, 40 + 60 * node_index]

class BrainView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(BrainView, self).__init__(
            parent, viewport_rect, viewport_rect.w, 1000)
        self._brain = None
        self.font = pygame.font.Font(None, 18)
        self.active_item = None
    
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
                neuron.connect_viewport(self)
                centre = neuron_centre(i, j)
                neuron.rect.x = centre[0] - neuron.rect.w // 2
                neuron.rect.y = centre[1] - neuron.rect.h // 2
                self.allneurons.add(neuron)

    def draw(self):
        brain = self._brain

        self.canvas.fill((0, 0, 0))
        
        if brain is None:
            self.image.blit(self.canvas, self.drag_offset)
            return

        input_labels = ('const', 'angle', 'speed', 'energy', 'tile_nut')
        hidden_labels = ()
        output_labels = ('angle ch', 'acc', 'eat', 'spawn')

        for i, layer in enumerate((input_labels, hidden_labels, output_labels)):
            for j, label in enumerate(layer):
                centrepos = neuron_centre(i, j)
                centrepos[0] -= 20
                centrepos[1] -= 30
                text = self.font.render(label, True, (255, 255, 255))
                self.canvas.blit(text, centrepos)

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
                    start = neuron_centre(i - 1, k)
                    end = neuron_centre(i, j)
                    pygame.draw.line(self.canvas, colour, start, end, 2)
                    if self.active_item:
                        text = self.font.render(
                            '%.2f' % weight, True, (255, 255, 255))
                        label_pos = (
                            start[0] + 23,
                            (start[1] + end[1]) // 2)
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

