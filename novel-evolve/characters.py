import math
import struct
import random
import operator
import time

import pygame
from pygame.locals import *

import genome

def sigmoid(x):
    try:
        return 1 / (1 + math.exp(-x))
    except OverflowError:
        return 0

class Neuron(pygame.sprite.Sprite):
    def __init__(self, input_weights, initial_value=None, fn=sigmoid):
        super(Neuron, self).__init__()
        self.fn = fn
        self.value = initial_value
        self.input_weights = input_weights[:]

    def process(self, inputs):
        self.value = sum(
            input_.value * weight
            for input_, weight in zip(inputs, self.input_weights))
        if self.fn is not None:
            self.value = self.fn(self.value)

    def __repr__(self):
        return "Neuron(%r, %r, %r)" % (self.input_weights, self.value, self.fn)

    def connect_viewport(self, viewport):
        self.image = pygame.Surface((40, 40), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()
        self.font = pygame.font.Font(None, 18)
        self.viewport = viewport

    def draw(self):
        centrepos = (20, 20)
        colour = 128, 255, 128
        if self.viewport.active_item is self:
            colour = 0, 255, 0
        pygame.draw.circle(self.image, colour, centrepos, 20, 0)
        text = self.font.render(str('%0.1f'%self.value), True, (0, 0, 0))
        rect = text.get_rect()
        textpos = centrepos[0] - rect.w // 2, centrepos[1] - rect.h // 2

        self.image.blit(text, textpos)


class Brain(object):
    def __init__(self, input_weights, output_weights):
        '''
        input_weights -- an array of len of hidden neurons, each item
            being an array of len of number of desired inputs.
            eg for two inputs and four hidden layer neurons:
                [ [1, 2], [2, 3], [4, 5], [5, 6] ]
        output_weights -- similar to input weights, but for the number of
            outputs and number of hidden layer neurons.
            eg for two outputs and four hidden layer neurons:
                [ [1, 2, 3, 4], [2, 3, 4, 5] ]
        '''
        self.input_weights = input_weights
        self.output_weights = output_weights
        num_inputs = input_weights and len(input_weights[0]) or 0
        self.inputs = [Neuron([], 0) for i in range(num_inputs)]
        self.hidden0 = []
        for neuron_input_weights in input_weights:
            self.hidden0.append(Neuron(neuron_input_weights))
        self.outputs = []
        for output_neuron_weights in output_weights:
            self.outputs.append(Neuron(output_neuron_weights, fn=lambda x: x**3))

    def process(self, *input_values):
        for neuron, input_value in zip(self.inputs, input_values):
            neuron.value = input_value
        for neuron in self.hidden0:
            neuron.process(self.inputs)
        for output in self.outputs:
            output.process(self.hidden0)
        return [output.value for output in self.outputs]

    def __repr__(self):
        return 'Brain(%r, %r)' % (self.input_weights, self.output_weights)


class NumpyBrain(object):
    '''Alternative implementation of Brain, using numpy matrix multiplication.

    API is identical but this one is oddly a lot slower than the Neuron-based
    brain. Unexpected....
    '''
    def __init__(self, input_weights, output_weights):
        self.input_weights = np.matrix(input_weights)
        self.output_weights = np.matrix(output_weights)
        self.sigmoid = np.vectorize(sigmoid)

    def process(self, *input_values):
        inputs = np.matrix([ [value] for value in input_values])
        hidden = self.sigmoid(self.input_weights * inputs)
        outputs = self.output_weights * hidden
        return [output.item(0) for output in outputs]

    def __repr__(self):
        return 'NumpyBrain(\n%r,\n%r)' % (self.input_weights, self.output_weights)

use_numpy = False
if use_numpy:
    import numpy as np
    Brain = NumpyBrain

class Character(pygame.sprite.Sprite):
    brain_inputs = 4
    brain_outputs = 3
    def __init__(self, world, radius):
        super(Character, self).__init__()

        self.world = world
        self.bred = 0

        # Physical properties
        self.r = radius   # radius, m
        self._x = None # x coord, m
        self._y = None # y coord, m
        self._created = 0.0 # age of world

        self._angle = math.pi / 2.0 # radians clockwise from north
        self._angle_change = 0.0

        self._speed = 0.0 # m/s
        self._acceleration = 0.0 # m/s^2

        self._energy = 300 # J
        self._energy_burn_rate = 25 # J/s
        self._age = 0.0 # s
        self.gen = 0
        self._spawn = 0.0 # > 0 means try to reproduce

        self.brain = None

        # Drawing
        if world:
            self._created = world.age
            self.image = pygame.Surface((self.r * 2 + 4, self.r * 2 + 4), SRCALPHA).convert_alpha()
            self.rect = self.image.get_rect()

    @classmethod
    def from_random(cls, world):
        g = genome.Genome.from_random(cls.brain_inputs, cls.brain_outputs)
        return cls.from_genome(world, g)

    @classmethod
    def from_genome(cls, world, genome):
        self = cls(world, genome.radius)
        num_hidden_neurons = genome.hidden_neurons
        input_weights = []
        output_weights = []
        pos = 2
        num_hidden0_weights = genome._inputs
        hidden0_weights_iter = iter(genome.hidden0_weights)
        for i in range(num_hidden_neurons):
            neuron_inputs = []
            for j in range(num_hidden0_weights):
                neuron_inputs.append(next(hidden0_weights_iter))
            input_weights.append(neuron_inputs)
        try:
            next(hidden0_weights_iter)
        except StopIteration:
            pass
        else:
            assert 0
        num_output_weights = genome._outputs
        output_weights_iter = iter(genome.output_weights)
        for i in range(num_output_weights):
            neuron_outputs = []
            for j in range(num_hidden_neurons):
                neuron_outputs.append(next(output_weights_iter))
            output_weights.append(neuron_outputs)
        try:
            next(output_weights_iter)
        except StopIteration:
            pass
        else:
            assert 0

        self.brain = Brain(input_weights, output_weights)
        self._genome = genome
        return self

    def _draw_border(self, colour):
        pygame.draw.lines(self.image, colour, 1, [
            (0, 0), (self.rect.w - 1, 0), (self.rect.w - 1, self.rect.h - 1), (0, self.rect.h - 1)
        ], 3)

    def draw(self):
        self.rect.x = self._x
        self.rect.y = self._y

        if self.world.active_item is not self:
            self._draw_border((0, 0, 0, 0))

        r_r = (self.r + 2, self.r + 2)
        liveness = int(min(1.0, self._energy / 500 + 0.5) * 255)
        pygame.draw.circle(self.image, (255, 255, 255), r_r, self.r + 2, 0)
        pygame.draw.circle(self.image, (liveness,liveness,0), r_r, self.r, 0)
        eye_pos = list(r_r)
        eye_pos[0] += int((self.r - 5) * math.sin(self._angle))
        eye_pos[1] -= int((self.r - 5) * math.cos(self._angle))
        pygame.draw.circle(self.image, (0, 0, 0), eye_pos, 3, 0)

        if self.world.active_item is self:
            self._draw_border((0, 0, 255, 255))

    def die(self):
        self.world.allcharacters.remove(self)
        if self.world.active_item is self:
            self.world.active_item = None

    def update(self, dt):
        world = self.world

        # observing world
        current_tile = world.alltiles_coords[self._x // world.tile_w, self._y // world.tile_h]

        # energy and age:
        self._age += dt
        self._energy -= self._energy_burn_rate * dt
        if self._energy <= 0:
            self.die()
            return

        # brain - update brain_inputs and brain_outputs above if changing
        inputs = (
            1,
            self._angle,
            self._speed,
            self._energy / 1000,
        )
        outputs = self.brain.process(*inputs)
        (
            self._angle_change,
            self._acceleration,
            self._spawn,
        ) = outputs

        # eating:
        foods = pygame.sprite.spritecollide(self, world.allfood, 0)
        for food in foods:
            self._energy += 25
            food.eaten()

        # reproducing:
        if self._spawn and self._energy > 350 and self._age > 3:
            self._energy -= 300
            newgenome = self._genome.mutate()
            newchar = self.__class__.from_genome(world, newgenome)
            newchar.x = self._x
            newchar.y = self._y
            newchar.bred = 1
            newchar.gen = self.gen + 1
            op = operator.sub
            while pygame.sprite.spritecollideany(newchar, world.allcharacters):
                newchar.x = op(newchar.x, 1)
                if newchar.x < 1:
                    op = operator.add
            world.allcharacters.add(newchar)

        # movement:
        prev_x, prev_y = self._x, self._y
        self._speed += (self._acceleration * dt)
        ddist = self._speed * dt
        self._angle = (self._angle + (self._angle_change * dt)) % (2 * math.pi)
        x = self._x + ddist * math.sin(self._angle)
        y = self._y - ddist * math.cos(self._angle)
        self.x = min(max(0, x), self.world.canvas_w - self.r)
        self.y = min(max(0, y), self.world.canvas_h - self.r)
        collided = pygame.sprite.spritecollide(self, world.allcharacters, 0)
        collided += pygame.sprite.spritecollide(self, world.alltrees, 0)
        for item in collided:
            if item is not self:
                self.x = prev_x
                self.y = prev_y
                self._speed = 0

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

    def __str__(self):
        return '\n'.join([
            "Character:",
            "created at: %.2fs" % self._created,
            "age: %.2fs" % self._age,
            "generation: %d" % self.gen,
            "spawn: %.2f" % self._spawn,
            "energy: %.2fJ" % self._energy,
            "r: %dm" % self.r,
            "angle: %.2f radians" % self._angle,
            "speed: %.2fm/s" % self._speed,
            "x: %dm E" % self._x,
            "y: %dm S" % self._y,
        ])

