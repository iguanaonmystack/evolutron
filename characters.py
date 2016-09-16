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
        self.inputs = inputs
        self.hidden0 = []
        for i in range(hidden_neurons):
            self.hidden0.append(Neuron(inputs))
        self.outputs = []
        for i in range(outputs):
            self.outputs.append(Neuron(hidden_neurons, fn=None))

    def process(self, *input_values):
        assert len(input_values) == self.inputs, (input_values, self.inputs)
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
        self._r = 25   # radius, m
        self._x = None # x coord, m
        self._y = None # y coord, m
        self._angle = math.pi / 2 * 3 # radians clockwise from north
        self._speed = 1 # m/s

        self._energy = 1000 # J
        self._energy_burn_rate = 50 # J/s
        self._age = 0.0 # s

        self.brain = Brain(4, 5, 3)

        # Drawing
        self.image = pygame.Surface((self._r * 2, self._r * 2), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()

    @property
    def colour(self):
        pass

    @colour.setter
    def colour(self, color):
       self.image.fill(color)
    
    def update(self, dt):
        # observing world
        current_tile = [
            t for t in self.world.alltiles
            if t.rect.collidepoint(self._x + self._r, self.y + self._r)][0]

        # energy and age:
        self._age += dt
        self._energy -= self._energy_burn_rate * dt
        if self._energy <= 0:
            self.world.allcharacters.remove(self)
            return

        # brain
        inputs = (
            self._angle,
            self._speed,
            self._energy,
            current_tile.nutrition,
        )
        outputs = (
            self._angle,
            self._speed,
            self._eating,
        ) = self.brain.process(*inputs)

        # eating:
        if self._eating > 0:
            eating_rate = 100 # J/s
            amount_to_eat = eating_rate * dt
            if current_tile.nutrition > amount_to_eat:
                self._energy += amount_to_eat
                current_tile.nutrition -= amount_to_eat

        # speed and position:
        prev_x, prev_y = self.x, self.y
        ddist = self._speed * dt
        self.x += ddist * math.sin(self._angle)
        self.y -= ddist * math.cos(self._angle)
        collided = pygame.sprite.spritecollide(self, self.world.allcharacters, 0)
        collided += pygame.sprite.spritecollide(self, self.world.allwalls, 0)
        for item in collided:
            if item is not self:
                self.x = prev_x
                self.y = prev_y
                self._speed = 0
    
        # drawing
        pygame.draw.circle(self.image, (0,255,0), (25,25), self._r, 0)
        eye_pos = [self._r, self._r]
        eye_pos[0] += int((self._r - 5) * math.sin(self._angle))
        eye_pos[1] -= int((self._r - 5) * math.cos(self._angle))
        pygame.draw.circle(self.image, (0, 0, 0), eye_pos, 3, 0)
    
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

    @property
    def r(self):
        return self._r
    
    @r.setter
    def r(self, value):
        self._r = value
    
    def __str__(self):
        return '\n'.join([
            "Character:",
            "age: %s" % self._age,
            "eating: %s" % self._eating,
            "energy: %s" % self._energy,
            "r: %s" % self._r,
            "angle: %s" % self._angle,
            "speed: %s" % self._speed,
            "x: %s" % self._x,
            "y: %s" % self._y,
        ])
