# cython: profile=True

import struct
import random
import operator
import time

from libc.math cimport sin, cos, exp, fabs
cdef extern from "errno.h":
    int errno

import pygame
from pygame.locals import *

import genome

# fast min/max functions:

cdef int int_min(int a, int b):
    return a if a < b else b

cdef int int_max(int a, int b):
    return a if a > b else b


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


# Line collision algorithm. Ref: https://stackoverflow.com/a/9997374 and 
# http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
cdef bint _ccw(int A_x, int A_y, int B_x, int B_y, int C_x, int C_y):
    return (C_y-A_y) * (B_x-A_x) > (B_y-A_y) * (C_x-A_x)

cdef bint intersect(int A_x, int A_y,
                    int B_x, int B_y,
                    int C_x, int C_y,
                    int D_x, int D_y):
    """Returns true if line segments AB and CD intersect"""
    return (
        _ccw(A_x, A_y, C_x, C_y, D_x, D_y) != _ccw(B_x, B_y, C_x, C_y, D_x, D_y)
    ) and (
        _ccw(A_x, A_y, B_x, B_y, C_x, C_y) != _ccw(A_x, A_y, B_x, B_y, D_x, D_y)
    )

# Point-in-triangle algorithm. Ref: https://stackoverflow.com/a/2049593
cdef int _sign(int p1_x, int p1_y, int p2_x, int p2_y, int p3_x, int p3_y):
    return (p1_x - p3_x) * (p2_y - p3_y) - (p2_x - p3_x) * (p1_y - p3_y);

cdef bint point_in_triangle(int pt_x, int pt_y,
                            int v1_x, int v1_y,
                            int v2_x, int v2_y,
                            int v3_x, int v3_y):
    cdef bint b1, b2, b3
    b1 = _sign(pt_x, pt_y, v1_x, v1_y, v2_x, v2_y) < 0
    b2 = _sign(pt_x, pt_y, v2_x, v2_y, v3_x, v3_y) < 0
    b3 = _sign(pt_x, pt_y, v3_x, v3_y, v1_x, v1_y) < 0
    return (b1 == b2) and (b2 == b3)



cdef bint line_in_triangle(int La_x, int La_y,
                           int Lb_x, int Lb_y,
                           int Ta_x, int Ta_y,
                           int Tb_x, int Tb_y,
                           int Tc_x, int Tc_y):
    """Returns true if Line La->Lb intersects or contained by triangle Ta-Tb-Tc"""
    # if either end of the line segment are inside the triangle, return True:
    if point_in_triangle(La_x, La_y, Ta_x, Ta_y, Tb_x, Tb_y, Tc_x, Tc_y):
        return True
    if point_in_triangle(Lb_x, Lb_y, Ta_x, Ta_y, Tb_x, Tb_y, Tc_x, Tc_y):
        return True

    # if line segment intersects either Ta-Tb or Ta-Tc, return True:
    # (don't need to check Tb-Tc since any line that intersects it
    #  will also intersect Ta-Tb or Ta-Tc)
    if intersect(La_x, La_y, Lb_x, Lb_y, Ta_x, Ta_y, Tb_x, Tb_y):
        return True
    if intersect(La_x, La_y, Lb_x, Lb_y, Ta_x, Ta_y, Tc_x, Tc_y):
        return True

    return False


# Main classes:

class Neuron(pygame.sprite.Sprite):

    def __init__(self, input_weights, initial_value=None, fn=sigmoid):
        super(Neuron, self).__init__()
        self.fn = fn
        self.raw_value = initial_value
        self.value = initial_value
        self.input_weights = input_weights[:]

    def process(self, inputs):
        cdef int i, inputs_len
        cdef double raw_value = 0.0
        inputs_len = len(inputs)
        for i in range(inputs_len):
            input_ = inputs[i]
            weight = self.input_weights[i]
            raw_value += input_.value * weight
        self.raw_value = raw_value
        self.value = self.fn(self.raw_value)

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
        text = self.font.render(
            str(self.value and '%0.1f'%self.value), True, (0, 0, 0))
        rect = text.get_rect()
        textpos = centrepos[0] - rect.w // 2, centrepos[1] - rect.h // 2

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
            'input_weights': self.input_weights,
        }
        return obj


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
        self.inputs = [Neuron([], 0, fn=identity) for i in range(num_inputs)]
        self.hidden0 = []
        for neuron_input_weights in input_weights:
            self.hidden0.append(Neuron(neuron_input_weights))
        self.outputs = []
        for output_neuron_weights in output_weights:
            self.outputs.append(Neuron(output_neuron_weights, fn=identity))

    def process(self, *input_values):
        for neuron, input_value in zip(self.inputs, input_values):
            neuron.value = input_value
        return self.reprocess()

    def reprocess(self):
        for neuron in self.hidden0:
            neuron.process(self.inputs)
        for output in self.outputs:
            output.process(self.hidden0)
        return [output.value for output in self.outputs]

    def __repr__(self):
        return 'Brain(%r, %r)' % (self.input_weights, self.output_weights)

    def dump(self):
        obj = {
            'input_weights': self.input_weights,
            'output_weights': self.output_weights,
            'inputs': [neuron.dump() for neuron in self.inputs],
            'hidden0': [neuron.dump() for neuron in self.hidden0],
            'outputs': [neuron.dump() for neuron in self.outputs],
        }
        return obj
    
    @classmethod
    def load(cls, obj):
        self = cls(obj['input_weights'], obj['output_weights'])
        return self


cdef class Character:
    cdef public object world
    cdef public object genome

    cdef public int haptic
    cdef public double vision_left
    cdef public double vision_right
    cdef public object seen_thing
    cdef int _vision_start_x, _vision_start_y
    cdef int _vision_left_end_x, _vision_left_end_y
    cdef int _vision_middle_end_x, _vision_middle_end_y
    cdef int _vision_right_end_x, _vision_right_end_y

    cdef public int r
    cdef public int x
    cdef public int y
    cdef public int prev_x
    cdef public int prev_y
    cdef public double height
    cdef public int created
    cdef public object tile

    cdef public double angle
    cdef public double speed
    cdef public double spawn
    cdef public int spawn_refractory

    cdef public float energy
    cdef public int age
    cdef public int gen
    cdef public int parents
    cdef public int children

    cdef public object brain

    cdef public object image
    cdef public object rect
    cdef public bint redraw

    brain_inputs = 5
    brain_outputs = 3

    # pygame compatibility (since we can't inherit Sprite from this cdef class)
    cdef object __g

    def __init__(self, world, radius):
        self.__g = {} # The groups the sprite is in

        self.world = world
        self.genome = None

        # Senses
        self.haptic = 0 # touching anything
        self.vision_left = 0 # Whether creature can see something
        self.vision_right = 0
        self.seen_thing = None

        # Physical properties
        self.r = radius   # radius, m
        self.x = -1 # x coord, m
        self.y = -1 # y coord, m
        self.prev_x = -1 # 
        self.prev_y = -1 # temporary while I sort out collisions
        self.height = 0.5 # used for vision
        self.created = 0 # age of world
        self.tile = None # set in update()

        self.angle = 0.0 # radians clockwise from north
        self.speed = 0.0 # m/tick
        self.spawn = 0.0
        self.spawn_refractory = 100

        self.energy = 2000 # J
        self.age = 0 # ticks
        self.gen = 0
        self.parents = 0
        self.children = 0

        self.brain = None

        # Drawing
        if world:
            self.created = world.age
            self.image = pygame.Surface((self.r * 2 + 4, self.r * 2 + 4), SRCALPHA).convert_alpha()
            self.rect = self.image.get_rect()
            self.redraw = True # ignored in Character

    @property
    def intersect_lines(self):
        rect = self.rect
        start = 0.2 + (self.r - 0.707) # add selection border width
                                       # and consider start/end pos re circle.
        end = rect.w - start
        return [
            ((rect.x + start, rect.y + start), (rect.x - end, rect.y - end)),
        ]

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
        self.genome = genome
        return self

    def _draw_border(self, colour):
        pygame.draw.lines(self.image, colour, 1, [
            (0, 0), (self.rect.w - 1, 0), (self.rect.w - 1, self.rect.h - 1), (0, self.rect.h - 1)
        ], 3)

    def draw(self):
        self.rect.x = self.x
        self.rect.y = self.y

        if self.world.active_item is not self:
            self._draw_border((0, 0, 0, 0))

        r_r = (self.r + 2, self.r + 2)
        liveness = int(min(1.0, (self.energy / 6000.) + 0.5) * 255)
        if self.parents == 1:
            pygame.draw.circle(self.image, (255, 255, 255), r_r, self.r + 2, 0)
        elif self.parents == 0:
            pygame.draw.circle(self.image, (128, 128, 128), r_r, self.r + 2, 0)
        else:
            pygame.draw.circle(self.image, (0, 0, 0), r_r, self.r + 2, 0)
        pygame.draw.circle(self.image, (liveness,liveness,0), r_r, self.r, 0)
        
        # eyes
        eye_pos = list(r_r)
        eye_pos[0] += int((self.r - 5) * sin(self.angle - 0.15))
        eye_pos[1] -= int((self.r - 5) * cos(self.angle - 0.15))
        pygame.draw.circle(
            self.image,
            (255 * self.vision_left ** 0.3, 0, 0),
            eye_pos,
            2,
            0)

        eye_pos = list(r_r)
        eye_pos[0] += int((self.r - 5) * sin(self.angle + 0.15))
        eye_pos[1] -= int((self.r - 5) * cos(self.angle + 0.15))
        pygame.draw.circle(
            self.image,
            (255 * self.vision_right ** 0.3, 0, 0),
            eye_pos,
            2,
            0)

        if self.world.active_item is self:
            self._draw_border((0, 0, 255, 255))

        #pygame.draw.line(self.world.canvas, (0,0,0), self._vision_start, self._vision_left_end)
        #pygame.draw.line(self.world.canvas, (0,0,0), self._vision_start, self._vision_middle_end)
        #pygame.draw.line(self.world.canvas, (0,0,0), self._vision_start, self._vision_right_end)

    def die(self):
        self.world.allcharacters.remove(self)
        if self.world.active_item is self:
            self.world.active_item = None
        if self.tile:
            self.tile.allcharacters.remove(self)

    cdef inline interactions(self, group):
        for item in group.spritedict:
            if item is self:
                continue
            for iline in item.intersect_lines:
                if (
                    self.vision_left == 0
                    and line_in_triangle(
                        iline[0][0], iline[0][1],
                        iline[1][0], iline[1][1],
                        self._vision_start_x, self._vision_start_y,
                        self._vision_left_end_x, self._vision_left_end_y,
                        self._vision_middle_end_x, self._vision_middle_end_y)
                ):
                    self.vision_left = item.height
                if (
                    self.vision_right == 0
                    and line_in_triangle(
                        iline[0][0], iline[0][1],
                        iline[1][0], iline[1][1],
                        self._vision_start_x, self._vision_start_y,
                        self._vision_middle_end_x, self._vision_middle_end_y,
                        self._vision_right_end_x, self._vision_right_end_y)
                ):
                    self.vision_right = item.height
                if self.vision_left != 0 and self.vision_right != 0:
                    return

    def update(self):
        cdef int i, j, x, y

        world = self.world

        # observing world
        tile_coord = self.x // world.tile_w, self.y // world.tile_h 
        try:
            tile = world.alltiles_coords[tile_coord]
        except KeyError:
            tile = None
        if tile is not None and tile is not self.tile:
            # tile changed
            oldtile = self.tile
            if oldtile is not None:
                oldtile.allcharacters.remove(self)
            tile.allcharacters.add(self)
            self.tile = tile
        check_tiles = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                coord = tile_coord[0] + i, tile_coord[1] + j
                try:
                    check_tiles.append(world.alltiles_coords[coord])
                except KeyError:
                    pass

        # vision triangle
        cdef int vr = 50
        cdef int vision_start_x = self.x + self.r + 2
        cdef int vision_start_y = self.y + self.r + 2
        vision_left_end_x = <int>(vision_start_x + (vr * sin(self.angle - 0.3)))
        vision_left_end_y = <int>(vision_start_y - (vr * cos(self.angle - 0.3)))
        vision_middle_end_x = <int>(vision_start_x + (vr * sin(self.angle)))
        vision_middle_end_y = <int>(vision_start_y - (vr * cos(self.angle)))
        vision_right_end_x = <int>(vision_start_x + (vr * sin(self.angle + 0.3)))
        vision_right_end_y = <int>(vision_start_y - (vr * cos(self.angle + 0.3)))

        #self._vision_start = vision_start_x, vision_start_y
        #self._vision_left_end = vision_left_end_x, vision_left_end_y
        #self._vision_middle_end = vision_middle_end_x, vision_middle_end_y
        #self._vision_right_end = vision_right_end_x, vision_right_end_y

        # age:
        self.age += 1

        # interaction with nearby objects:
        foods = []
        for tile in check_tiles:
            foods.extend(pygame.sprite.spritecollide(self, tile.allfood, 0))
            self.interactions(tile.allfood)
            self.interactions(tile.alltrees)
            self.interactions(tile.allcharacters)

        # eating:
        cdef int food_energy
        for food in foods:
            food_energy = food.energy
            self.energy += food_energy
            food.eaten()

        # brain - update brain_inputs and brain_outputs above if changing
        inputs = (
            1,
            self.vision_left,
            self.vision_right,
            self.haptic,
            self.energy / 10000,
        )
        cdef double angle_change
        cdef double Fmove
        outputs = self.brain.process(*inputs)
        (
            angle_change,
            Fmove,
            self.spawn,
        ) = outputs
        # compensate values from NN
        angle_change /= 2

        self.energy -= fabs(Fmove * 5) + 10
        if self.energy <= 0:
            self.die()
            return

        # asexual reproduction:
        cdef Character newchar
        if self.spawn > 0.5 and self.energy > 3000 and self.spawn_refractory == 0:
            self.energy -= 3000
            self.spawn_refractory = 60
            newgenome = self.genome.mutate()
            newchar = Character.from_genome(world, newgenome)
            newchar.x = self.x
            newchar.rect.x = self.rect.x
            newchar.y = self.y
            newchar.rect.y = self.rect.y
            newchar.gen = self.gen + 1
            newchar.parents = 1
            self.children += 1
            op = operator.sub
            while pygame.sprite.spritecollideany(newchar, world.allcharacters)\
                or pygame.sprite.spritecollideany(newchar, world.alltrees):
                x = op(newchar.x, 2)
                newchar.x = x
                newchar.rect.x = x
                if newchar.x < 1:
                    op = operator.add
            world.allcharacters.add(newchar)

        if self.spawn_refractory > 0:
            self.spawn_refractory -= 1

        # movement:
        Ffriction = self.speed / 4
        acceleration = (Fmove - Ffriction) / (self.r)
        self.prev_x, self.prev_y = self.x, self.y
        self.speed += acceleration
        cdef double ddist = self.speed
        cdef int canvas_w = world.canvas_w
        cdef int canvas_h = world.canvas_h
        self.angle = (self.angle + angle_change) % 6.283185307179586
        x = self.x + <int>(ddist * sin(self.angle))
        y = self.y - <int>(ddist * cos(self.angle))
        self.x = int_min(int_max(0, x), canvas_w - self.r)
        self.y = int_min(int_max(0, y), canvas_h - self.r)
        collided = []
        for tile in check_tiles:
            collided.extend(pygame.sprite.spritecollide(self, tile.alltrees, 0))
        for item in collided:
            self.x = self.prev_x
            self.y = self.prev_y
            self.speed = 0
            self.haptic = 1
            break
        else:
            self.haptic = 0 # may still be updated by Group.collisions()


    def __repr__(self):
        return '<Char at {},{}>'.format(self.x, self.y)

    def __str__(self):
        return '\n'.join([
            "Character:",
            "created at: %dt" % self.created,
            "age: %dt" % self.age,
            "generation: %d" % self.gen,
            "energy: %.2fJ" % self.energy,
            "r: %dm" % self.r,
            "angle: %.2f radians" % self.angle,
            "speed: %.2fm/t" % self.speed,
            "vision: %r" % self.seen_thing,
            "children: %s" % self.children,
            "x: %dm E" % self.x,
            "y: %dm S" % self.y,
        ])

    def dump(self):
        obj = {
            'r': self.r,
            'x': self.x,
            'y': self.y,
            'created': self.created,
            'angle': self.angle,
            'speed': self.speed,
            'energy': self.energy,
            'age': self.age,
            'gen': self.gen,
            'brain': self.brain.dump(),
            'genome': self.genome.dump(),
        }
        return obj
    
    @classmethod
    def load(cls, obj):
        self = cls(None, obj['r'])
        self.x = obj['x']
        self.y = obj['y']
        self.created = obj['created']
        self.angle = obj['angle']
        self.speed = obj['speed']
        self.energy = obj['energy']
        self.age = obj['age']
        self.gen = obj['gen']
        self.brain = Brain.load(obj['brain'])
        #self.genome = genome.Genome.load(obj['genome'])
        return self


    # pygame comptibility:

    def add_internal(self, group):
        self.__g[group] = 0

    def remove_internal(self, group):
        del self.__g[group]

