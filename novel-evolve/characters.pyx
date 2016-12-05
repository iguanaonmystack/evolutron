# cython: profile=True
cimport cython

import struct
import random
import operator
import time

from cpython cimport array
from array import array
from libc.math cimport sin, cos, exp, fabs
cdef extern from "errno.h":
    int errno

import pygame
from pygame.locals import *

import genome
from sprite cimport Sprite
from neuron cimport Neuron
from neuron import identity

from characters cimport Character, Brain

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

cdef class Brain:
    def __cinit__(self, input_weights, output_weights):
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
        self.inputs = [Neuron(array('d', []), 0, fn=identity) for i in range(num_inputs)]
        self.hidden0 = []
        for neuron_input_weights in input_weights:
            self.hidden0.append(Neuron(array('d', neuron_input_weights)))
        self.outputs = []
        for output_neuron_weights in output_weights:
            self.outputs.append(Neuron(array('d', output_neuron_weights), fn=identity))

    cdef process(self, double[:] input_values):
        cdef int i
        cdef Neuron neuron
        inputs = self.inputs
        for i in range(len(inputs)):
            neuron = inputs[i]
            neuron.value = input_values[i]
        return self.reprocess()

    cpdef reprocess(self):
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


cdef class Character(Sprite):
    brain_inputs = 5
    brain_outputs = 3

    def __cinit__(self, object world, int radius):
        self.world = world
        self.genome = None

        # Senses
        self.haptic = 0 # touching anything
        self.vision_left = 0 # Whether creature can see something
        self.vision_right = 0

        # Physical properties
        self.r = radius   # radius, m
        self.midx = -1
        self.midy = -1 # floating point coords, middle of creature
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
            self.image = pygame.Surface((self.r * 2, self.r * 2), SRCALPHA).convert_alpha()
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
        return Character.from_genome(world, g)

    @classmethod
    def from_genome(cls, world, genome):
        self = Character(world, genome.radius)
        self.load_genome(genome)
        return self

    cdef void load_genome(Character self, object genome):
        self.r = genome.radius
        if self.world is not None:
            self.image = pygame.Surface((self.r * 2, self.r * 2), SRCALPHA).convert_alpha()
            self.rect = self.image.get_rect()
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

    cdef void _draw_border(self, colour):
        pygame.draw.lines(self.image, colour, 1, [
            (0, 0), (self.rect.w - 1, 0), (self.rect.w - 1, self.rect.h - 1), (0, self.rect.h - 1)
        ], 3)

    def draw(self):
        if self.world.active_item is not self:
            self._draw_border((0, 0, 0, 0))

        r_r = (self.r, self.r)
        liveness = int(min(1.0, (self.energy / 6000.) + 0.5) * 255)
        if self.parents == 1:
            pygame.draw.circle(self.image, (255, 255, 255), r_r, self.r, 0)
        elif self.parents == 0:
            pygame.draw.circle(self.image, (128, 128, 128), r_r, self.r, 0)
        else:
            pygame.draw.circle(self.image, (0, 0, 0), r_r, self.r, 0)
        pygame.draw.circle(self.image, (liveness,liveness,0), r_r, self.r - 2, 0)
        
        # eyes
        eye_pos = list(r_r)
        eye_pos[0] += int((self.r - 5) * sin(self.angle - 0.2))
        eye_pos[1] -= int((self.r - 5) * cos(self.angle - 0.2))
        pygame.draw.circle(
            self.image,
            (255 * self.vision_left ** 0.3, 0, 0),
            eye_pos,
            2,
            0)

        eye_pos = list(r_r)
        eye_pos[0] += int((self.r - 5) * sin(self.angle + 0.2))
        eye_pos[1] -= int((self.r - 5) * cos(self.angle + 0.2))
        pygame.draw.circle(
            self.image,
            (255 * self.vision_right ** 0.3, 0, 0),
            eye_pos,
            2,
            0)

        if self.world.active_item is self:
            self._draw_border((0, 0, 255, 255))

        #pygame.draw.line(self.world.canvas, (0,0,0), (self._vision_start_x, self._vision_start_y), (self._vision_left_end_x, self._vision_left_end_y))
        #pygame.draw.line(self.world.canvas, (0,0,0), (self._vision_start_x, self._vision_start_y), (self._vision_middle_end_x, self._vision_middle_end_y))
        #pygame.draw.line(self.world.canvas, (0,0,0), (self._vision_start_x, self._vision_start_y), (self._vision_right_end_x, self._vision_right_end_y))

    cpdef void die(self):
        self.world.allcharacters.remove(self)
        if self.world.active_item is self:
            self.world.active_item = None
        if self.tile:
            self.tile.allcharacters.remove(self)

    cdef inline void interactions(self, group):
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

    @cython.cdivision(True)
    def update(self):
        cdef int i, j
        cdef double x, y

        world = self.world

        # observing world
        tile_coord = self.midx // world.tile_w, self.midy // world.tile_h 
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
        self._vision_start_x = <int>self.midx
        self._vision_start_y = <int>self.midy
        self._vision_left_end_x = <int>(
            self._vision_start_x + (vr * sin(self.angle - 0.4)))
        self._vision_left_end_y = <int>(
            self._vision_start_y - (vr * cos(self.angle - 0.4)))
        self._vision_middle_end_x = <int>(
            self._vision_start_x + (vr * sin(self.angle)))
        self._vision_middle_end_y = <int>(
            self._vision_start_y - (vr * cos(self.angle)))
        self._vision_right_end_x = <int>(
            self._vision_start_x + (vr * sin(self.angle + 0.4)))
        self._vision_right_end_y = <int>(
            self._vision_start_y - (vr * cos(self.angle + 0.4)))

        # age:
        self.age += 1

        # interaction with nearby objects:
        foods = []
        self.vision_left = 0
        self.vision_right = 0
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
        cdef double[:] inputs = array('d', [
            1,
            self.vision_left,
            self.vision_right,
            self.haptic,
            self.energy / 10000,
        ])
        cdef double angle_change
        cdef double Fmove
        outputs = self.brain.process(inputs)
        (
            angle_change,
            Fmove,
            self.spawn,
        ) = outputs
        # compensate values from NN
        angle_change /= 2

        Fmove = fabs(Fmove)
        self.energy -= Fmove * 5 + 10
        if self.energy <= 0:
            self.die()
            return

        # asexual reproduction:
        if self.spawn > 0.5 and self.energy > 5000 and self.spawn_refractory == 0:
            self.spawn_asex()

        if self.spawn_refractory > 0:
            self.spawn_refractory -= 1

        # movement:
        Ffriction = self.speed / 4
        acceleration = (Fmove - Ffriction) / (self.r)
        self.speed += acceleration
        cdef double ddist = self.speed
        cdef int canvas_w = world.canvas_w
        cdef int canvas_h = world.canvas_h
        self.angle = (self.angle + angle_change) % 6.283185307179586
        x = self.midx + (ddist * sin(self.angle))
        y = self.midy - (ddist * cos(self.angle))
        self.set_midpoint_x(double_min(double_max(self.r, x), canvas_w - self.r))
        self.set_midpoint_y(double_min(double_max(self.r, y), canvas_h - self.r))
        collided = []
        for tile in check_tiles:
            collided.extend(pygame.sprite.spritecollide(self, tile.alltrees, 0))
        cdef double midpoint_x, midpoint_y
        for tree in collided:
            midpoint_x = (self.midx + tree.midx) / 2
            midpoint_y = (self.midy + tree.midy) / 2
            if midpoint_x != self.midx:
                self.set_midpoint_x(self.midx + 10 / (self.midx - midpoint_x))
            if midpoint_y != self.midy:
                self.set_midpoint_y(self.midy + 10 / (self.midy - midpoint_y))

            self.speed = 0
            self.haptic = 1
            break
        else:
            self.haptic = 0 # may still be updated by Group.collisions()
    
    cpdef void spawn_asex(self):
        cdef Character newchar
        self.energy -= 5000
        self.spawn_refractory = 60
        newgenome = self.genome.mutate()
        newchar = Character(self.world, 0)
        newchar.load_genome(newgenome)
        newchar.set_midpoint_x(self.midx)
        newchar.set_midpoint_y(self.midy)
        newchar.gen = self.gen + 1
        newchar.parents = 1
        newchar.energy = 4000
        self.children += 1
        self.world.allcharacters.add(newchar)

    cpdef void set_midpoint_x(self, double x):
        self.midx = x
        self.rect.x = x - 2 - self.r

    cpdef void set_midpoint_y(self, double y):
        self.midy = y
        self.rect.y = y - 2 - self.r

    def __repr__(self):
        return '<Char at {},{}>'.format(self.rect.x, self.rect.y)

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
            "children: %s" % self.children,
            "x: %dm E" % self.midx,
            "y: %dm S" % self.midy,
        ])

    def dump(self):
        obj = {
            'r': self.r,
            'x': self.rect.x,
            'y': self.rect.y,
            'created': self.created,
            'angle': self.angle,
            'speed': self.speed,
            'spawn_refractory': self.spawn_refractory,
            'energy': self.energy,
            'age': self.age,
            'gen': self.gen,
            'parents': self.parents,
            'children': self.children,
            'brain': self.brain.dump(),
            'genome': self.genome.dump(),
        }
        return obj
    
    @classmethod
    def load(cls, obj):
        self = cls(None, obj['r'])
        if self.rect is not None:
            self.rect.x = obj['x']
            self.rect.y = obj['y']
        self.created = obj['created']
        self.angle = obj['angle']
        self.speed = obj['speed']
        self.spawn_refractory = obj['spawn_refractory']
        self.energy = obj['energy']
        self.age = obj['age']
        self.gen = obj['gen']
        self.parents = obj['parents']
        self.children = obj['children']
        self.brain = Brain.load(obj['brain'])
        #self.genome = genome.Genome.load(obj['genome'])
        return self



