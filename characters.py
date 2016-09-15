import math
import random

import pygame
from pygame.locals import *

def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0

class Neuron(object):
    def __init__(self, input_count, initial_value=None, fn=sigmoid):
        self.input_count = input_count
        self.fn = fn
        self.value = initial_value
        self.input_weights = []
        for i in range(input_count):
            self.input_weights.append(random.random() * 2 - 1)

    def process(self, inputs):
        assert len(inputs) == self.input_count
        self.value = sum(
            inputs[i].value * self.input_weights[i]
            for i in range(self.input_count))
        if self.fn is not None:
            self.value = self.fn(self.value)

    def __repr__(self):
        return "Neuron(%r, %r) <%r>" % (self.input_count, self.value, self.input_weights)

class Brain(object):
    def __init__(self, inputs=2, hidden_neurons=5, outputs=1):
        self.hidden0 = []
        for i in range(hidden_neurons):
            self.hidden0.append(Neuron(inputs))
        self.outputs = []
        for i in range(outputs):
            self.outputs.append(Neuron(hidden_neurons, fn=None))

    def process(self, *input_values):
        inputs = [Neuron(0, value) for value in input_values]
        for neuron in self.hidden0:
            neuron.process(inputs)
        for output in self.outputs:
            output.process(self.hidden0)
        return [output.value for output in self.outputs]

class Character(pygame.sprite.Sprite):
    def __init__(self, world):
        super(Character, self).__init__()

        self.world = world

        # Physical properties
        self.r = 25  # radius
        self._x = None
        self._y = None
        self.dx = 0
        self.dy = 0

        self.brain = Brain(2, 5, 2)

        # Drawing
        self.image = pygame.Surface((self.r * 2, self.r * 2), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()

    @property
    def colour(self):
        pass

    @colour.setter
    def colour(self, color):
       self.image.fill(color)
    
    def update(self):
        self.dx, self.dy = self.brain.process(self._x, self._y)
        print self._x, self._y, self.dx, self.dy
        self.x += self.dx
        self.y += self.dy
        collided = pygame.sprite.spritecollide(self, self.world.allcharacters, 0)
        collided += pygame.sprite.spritecollide(self, self.world.allwalls, 0)
        for item in collided:
            if item is not self:
                self.x -= self.dx
                self.y -= self.dy
                self.dx = 0 #-self.dx
                self.dy = 0 #-self.dy

        pygame.draw.circle(self.image, (0,255,0), (25,25), self.r, 0)
    
    @property
    def x(self):
        return self._x
    
    @x.setter
    def x(self, value):
        self._x = value
        self.rect.x = value    

    @property
    def y(self):
        return self._y
    
    @y.setter
    def y(self, value):
        self._y = value
        self.rect.y = value

