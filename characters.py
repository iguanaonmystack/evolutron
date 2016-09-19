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


class Character(pygame.sprite.Sprite):
    brain_inputs = 5
    brain_outputs = 4
    def __init__(self, world):
        super(Character, self).__init__()

        self.world = world

        # Physical properties
        self.r = 25   # radius, m
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
            self.image = pygame.Surface((self.r * 2, self.r * 2), SRCALPHA).convert_alpha()
            self.rect = self.image.get_rect()

    @classmethod
    def from_genome(cls, world, genome):
        self = cls(world)
        
        genedata = genome.data
        self.r = int(genedata[0])
        num_hidden_neurons = genedata[1]
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
        pygame.draw.circle(self.image, (255,255,0), (self.r, self.r), self.r, 0)
        eye_pos = [self.r, self.r]
        eye_pos[0] += int((self.r - 5) * math.sin(self._angle))
        eye_pos[1] -= int((self.r - 5) * math.cos(self._angle))
        pygame.draw.circle(self.image, (0, 0, 0), eye_pos, 3, 0)
        font = pygame.font.Font(None, 24)
        text = font.render(str(self._energy), True, (0, 0, 0))
        self.image.blit(text, (self.r, self.r))

    def die(self):
        self.world.allcharacters.remove(self)

    def update(self, dt):
        world = self.world

        # observing world
        if self._x < 0 or self._y < 0 \
        or self._x > world.w or self._y > world.h:
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
        self.x += ddist * math.sin(self._angle)
        self.y -= ddist * math.cos(self._angle)
        collided = pygame.sprite.spritecollide(self, world.allcharacters, 0)
        collided += pygame.sprite.spritecollide(self, world.allwalls, 0)
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

