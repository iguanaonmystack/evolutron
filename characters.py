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

class Neuron(object):
    def __init__(self, input_weights, initial_value=None, fn=sigmoid):
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
        return "Neuron(%r, %r) <%r>" % (self.input_weights, self.value, self.input_weights)
    


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
        self.hidden0 = []
        for neuron_input_weights in input_weights:
            self.hidden0.append(Neuron(neuron_input_weights))
        self.outputs = []
        for output_neuron_weights in output_weights:
            self.outputs.append(Neuron(output_neuron_weights, fn=None))

    def process(self, *input_values):
        inputs = [Neuron([], value) for value in input_values]
        for neuron in self.hidden0:
            neuron.process(inputs)
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
    brain_inputs = 5
    brain_outputs = 4
    def __init__(self, world, radius):
        super(Character, self).__init__()

        self.world = world

        # Physical properties
        self.r = radius   # radius, m
        self._x = None # x coord, m
        self._y = None # y coord, m
        self._angle = math.pi / 2 # radians clockwise from north
        self._speed = 1 # m/s

        self._energy = 500 # J
        self._energy_burn_rate = 50 # J/s
        self._age = 0.0 # s
        self._eating = 0.0 # > 0 means eat
        self._spawn = 0.0 # > 0 means try to reproduce

        self.brain = None

        # Drawing
        if world:
            self.image = pygame.Surface((self.r * 2 + 4, self.r * 2 + 4), SRCALPHA).convert_alpha()
            self.rect = self.image.get_rect()

    @classmethod
    def from_genome(cls, world, genome):
        
        genedata = genome.data
        self = cls(world, int(genedata[0]))
        num_hidden_neurons = int(genedata[1])
        input_weights = []
        output_weights = []
        pos = 2
        for i in range(num_hidden_neurons):
            row = []
            for j in range(cls.brain_inputs):
                data = genome.data[pos:pos + 1]
                value = 0
                if len(data) == 1:
                    value = data[0]
                row.append(value)
                pos += 1
            input_weights.append(row)
        for i in range(cls.brain_outputs):
            row = []
            for j in range(num_hidden_neurons):
                data = genome.data[pos:pos + 1]
                value = 0
                if len(data) == 1:
                    value = data[0]
                row.append(value)
                pos += 1
            output_weights.append(row)

        self.brain = Brain(input_weights, output_weights)
        self._genome = genome
        return self

    @property
    def colour(self):
        pass

    @colour.setter
    def colour(self, color):
       self.image.fill(color)
    
    def draw(self):
        self.rect.x = self._x
        self.rect.y = self._y
        r_r = (self.r + 2, self.r + 2)
        liveness = int(min(1.0, self._energy / 2000 + 0.5) * 255)
        pygame.draw.circle(self.image, (liveness,liveness,0), r_r, self.r, 0)
        eye_pos = list(r_r)
        eye_pos[0] += int((self.r - 5) * math.sin(self._angle))
        eye_pos[1] -= int((self.r - 5) * math.cos(self._angle))
        pygame.draw.circle(self.image, (0, 0, 0), eye_pos, 3, 0)

        if self.world.active_item is self:
            border = (0, 0, 255, 255)
        else:
            border = (0, 0, 0, 0)
        pygame.draw.lines(self.image, border, 1, [
            (0, 0), (self.rect.w - 1, 0), (self.rect.w - 1, self.rect.h - 1), (0, self.rect.h - 1)
        ], 3)

    def die(self):
        self.world.allcharacters.remove(self)

    def update(self, dt):
        world = self.world

        # observing world
        if self._x < 0 or self._y < 0 \
        or self._x > world.canvas_w or self._y > world.canvas_h:
            self.die()
            return
        else:
            current_walls = [
                t for t in world.allwalls
                if t.rect.collidepoint(self._x + self.r, self.y + self.r)]
            if current_walls:
                # oops, off the map
                self.die()
                return
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
            self._energy,
            current_tile.nutrition,
        )
        outputs = self.brain.process(*inputs)
        (
            self._angle,
            self._speed, # TODO this should be acceleration
            self._eating,
            self._spawn,
        ) = outputs

        # eating:
        if self._eating > 0:
            eating_rate = 100 # J/s
            amount_to_eat = eating_rate * dt
            if current_tile.nutrition > amount_to_eat:
                self._energy += amount_to_eat
                current_tile.nutrition -= amount_to_eat
        
        # reproducing
        if self._spawn > 0:
            if self._energy > 1000:
                self._energy -= 1000
                print "spawning new character"
                newgenome = self._genome.mutate()
                newchar = self.__class__.from_genome(world, newgenome)
                newchar.x = self._x
                newchar.y = self._y
                op = operator.sub
                while pygame.sprite.spritecollideany(newchar, world.allcharacters):
                    newchar.x = op(newchar.x, 1)
                    if newchar.x < 1:
                        op = operator.add
                world.allcharacters.add(newchar)

        # speed and position:
        prev_x, prev_y = self._x, self._y
        ddist = self._speed * dt
        x = self._x + ddist * math.sin(self._angle)
        y = self._y - ddist * math.cos(self._angle)
        self.x = min(max(0, x), self.world.canvas_w - self.r)
        self.y = min(max(0, y), self.world.canvas_h - self.r)
        collided = pygame.sprite.spritecollide(self, world.allcharacters, 0)
        collided += pygame.sprite.spritecollide(self, world.allwalls, 0)
        for item in collided:
            if item is not self:
                self.x = prev_x
                self.y = prev_y
    
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
            "age: %s" % self._age,
            "eating: %s" % self._eating,
            "spawn: %s" % self._spawn,
            "energy: %s" % self._energy,
            "r: %s" % self.r,
            "angle: %s" % self._angle,
            "speed: %s" % self._speed,
            "x: %s" % self._x,
            "y: %s" % self._y,
        ])

