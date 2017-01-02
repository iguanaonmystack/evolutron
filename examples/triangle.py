"""Triangle boundary examples"""

from __future__ import division
import sys
import time
import random
from collections import deque

import pygame
from pygame.locals import *

# Point-in-triangle algorithm. Ref: https://stackoverflow.com/a/2049593
def _sign(p1, p2, p3):
    return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1]);

def point_in_triangle(pt, v1, v2, v3):
    b1 = _sign(pt, v1, v2) < 0
    b2 = _sign(pt, v2, v3) < 0
    b3 = _sign(pt, v3, v1) < 0
    return (b1 == b2) and (b2 == b3)

# Line collision algorithm. Ref: https://stackoverflow.com/a/9997374 and 
# http://www.bryceboe.com/2006/10/23/line-segment-intersection-algorithm/
def _ccw(A, B, C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])

def intersect(A,B,C,D):
    """Returns true if line segments AB and CD intersect"""
    return _ccw(A,C,D) != _ccw(B,C,D) and _ccw(A,B,C) != _ccw(A,B,D)



def line_in_triangle(La, Lb, Ta, Tb, Tc):
    """Returns true if Line La->Lb intersects or contained by triangle Ta-Tb-Tc"""
    if point_in_triangle(La, Ta, Tb, Tc) or point_in_triangle(Lb, Ta, Tb, Tc):
        return True
    if intersect(La, Lb, Ta, Tb) or intersect(La, Lb, Ta, Tc):
        # don't need to check Tb-Tc since any line that intersects it
        # will also intersect Ta-Tb or Ta-Tc
        return True
    return False


class Window():
    """Logical representation of the application window."""

    def __init__(self, screen):

        self.screen = screen
        self.w, self.h = screen.get_size()
        self.onresize(self.w, self.h)

        self.triangle()
        self.line = [(0, 0), (0, 0)]
        self.newline = [None, None]
        self.inside = False
        self.font = pygame.font.SysFont('monospace', 18)
        self.calc_time = deque()

    def onresize(self, window_w, window_h):
        self.background = pygame.Surface(self.screen.get_size()).convert()

    def update(self):
        t1 = time.time()
        self.inside = line_in_triangle(self.line[0], self.line[1], self.A, self.B, self.C)
        t2 = time.time()
        self.calc_time.append(t2 - t1)
        while len(self.calc_time) > 20:
            self.calc_time.popleft()


    def frame(self):
        self.background.fill((0, 0, 0))
        pygame.draw.line(self.background, (255, 255, 0), self.line[0], self.line[1], 1)

        pygame.draw.lines(self.background, (255, 255, 255), 1, [
            self.A, self.B, self.B, self.C, self.C, self.A
        ], 1)

        self.screen.blit(self.background, (0, 0))

        label = self.font.render(str(self.inside), 1, (255, 255, 0))
        screen.blit(label, (100, 100))
        label = self.font.render(str(sum(self.calc_time) / len(self.calc_time)), 1, (255, 255, 0))
        screen.blit(label, (100, 200))

        pygame.display.flip()


    def onmousedown(self, screenpos, button):
        self.newline[0] = screenpos

    def onmouseup(self, screenpos, button):
        self.newline[1] = screenpos
        self.line = self.newline
        self.newline = [None, None]

    def triangle(self):
        self.A = random.randint(0, self.w), random.randint(0, self.h)
        self.B = random.randint(0, self.w), random.randint(0, self.h)
        self.C = random.randint(0, self.w), random.randint(0, self.h)

flags = RESIZABLE
pygame.init()
screen = pygame.display.set_mode((1280, 720), flags, 32)
window = Window(screen)

while 1:
    time.sleep(0.1)
    
    window.update()
    window.frame()

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            mousedown_pos = event.dict['pos']
            button = event.dict['button'] #1/2/3=left/middle/right, 4/5=wheel
            window.onmousedown(mousedown_pos, button)
        elif event.type == MOUSEBUTTONUP:
            pos = event.dict['pos']
            button = event.dict['button'] #1/2/3=left/middle/right, 4/5=wheel
            window.onmouseup(pos, button)
        elif event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                sys.exit()
            elif event.key  == K_r:
                window.triangle()

