
import pygame
from pygame.locals import *

import viewport

def neuron_centre(layer, node_index):
    return (20 + 75 * layer, 20 + 60 * node_index)

class BrainView(viewport.Viewport):

    def __init__(self, parent, viewport_rect):
        super(BrainView, self).__init__(
            parent, viewport_rect, viewport_rect.w, viewport_rect.h)
        self.brain = None
        self.font = pygame.font.Font(None, 18)
    
    def draw(self):
        brain = self.brain
        if brain is None:
            return

        self.canvas.fill((0, 0, 0))

        for i, layer in enumerate((brain.inputs, brain.hidden0, brain.outputs)):
            for j, neuron in enumerate(layer):

                for k, weight in enumerate(neuron.input_weights):
                    colour = (int(weight * 256),) * 3

                    start = neuron_centre(i - 1, k)
                    end = neuron_centre(i, j)
                    pygame.draw.line(self.canvas, colour, start, end, 2)

        for i, layer in enumerate((brain.inputs, brain.hidden0, brain.outputs)):
            for j, neuron in enumerate(layer):

                centrepos = neuron_centre(i, j)
                pygame.draw.circle(self.canvas, (128, 255, 128), centrepos, 20, 0)

                text = self.font.render(str('%0.1f'%neuron.value), True, (0, 0, 0))
                rect = text.get_rect()
                textpos = centrepos[0] - rect.w // 2, centrepos[1] - rect.h // 2
                self.canvas.blit(text, textpos)

        self.image.blit(self.canvas, self.drag_offset)

