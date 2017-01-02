from libc.math cimport sin, cos, exp, fabs
cdef extern from "errno.h":
    int errno
 
from cpython cimport array
import pygame
from pygame import Rect

from sprite cimport Sprite
from neuron cimport Neuron

# Neuron activation functions:

def sigmoid(double x):
    errno = 0
    cdef double exp_minus_x = exp(-x)
    if exp_minus_x == 0 and errno:
        return 0
    return 1 / (1 + exp_minus_x)

def identity(x):
    return x

def cube(x):
    return x**3

# Main class:

cdef class Neuron(Sprite):
    def __init__(self, double[:] input_weights, initial_value=-1, fn=sigmoid):
        Sprite.__init__(self)
        self.fn = fn
        self.raw_value = initial_value
        self.value = initial_value
        self.input_weights = input_weights[:]

    def process(self, list inputs):
        cdef int i
        cdef Neuron input_
        cdef double weight
        cdef double raw_value = 0.0
        for i in range(len(inputs)):
            input_ = inputs[i]
            weight = self.input_weights[i]
            raw_value += input_.value * weight
        self.raw_value = raw_value
        self.value = self.fn(self.raw_value)

    def connect_viewport(self, viewport, neuron_width, neuron_height, neuron_centre):
        self.image = pygame.Surface((neuron_width, neuron_height), pygame.locals.SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.x = neuron_centre[0] - neuron_width // 2
        self.rect.y = neuron_centre[1] - neuron_height // 2
        self.font = pygame.font.Font(None, 18)
        self.viewport = viewport

    def draw(self):
        colour = 128, 255, 128
        if self.viewport.active_item is self:
            colour = 0, 255, 0
        rect = Rect(0, 0, self.rect.w, self.rect.h)
        pygame.draw.ellipse(self.image, colour, rect, 0)
        text = self.font.render(
            str(self.value and '%0.1f'%self.value), True, (0, 0, 0))
        textrect = text.get_rect()
        textpos = (self.rect.w // 2) - (textrect.w // 2), (self.rect.h // 2) - (textrect.h // 2)

        self.image.blit(text, textpos)

    def __repr__(self):
        return "Neuron(%r, %r, %r)" % (self.input_weights, self.value, self.fn)

    def __str__(self):
        lines = [
            'Neuron:',
            'Current value: %r' % self.value,
            'Activation function: %r' % self.fn.__name__,
            'Input weights:'
        ]
        weight_sum = 0
        for i, input_weight in enumerate(self.input_weights):
            lines.append('    %d: %r' % (i, input_weight))
            weight_sum += input_weight
        lines.append('Sum wt[i] * input[i]: %r' % self.raw_value)
        return '\n'.join(lines)

    def dump(self):
        obj = {
            'fn': self.fn.__name__,
            'value': self.value,
            'input_weights': list(self.input_weights),
        }
        return obj


