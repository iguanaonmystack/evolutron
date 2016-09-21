import pygame
from pygame.locals import *

class Viewport(pygame.sprite.Sprite):

    def __init__(self, parent, viewport_rect, canvas_w, canvas_h):
        super(Viewport, self).__init__()

        self.parent = parent
        self.resize(viewport_rect)

        self.canvas = pygame.Surface((canvas_w, canvas_h)).convert()
        self.drag_offset = [0, 0]
    
    def resize(self, viewport_rect):
        '''Resize the viewport'''
        self.image = pygame.Surface((viewport_rect.w, viewport_rect.h)).convert()
        self.rect = viewport_rect
    
    @property
    def canvas_w(self):
        return self.canvas.get_width()
    @canvas_w.setter
    def canvas_w(self, val):
        self.canvas = pygame.Surface((val, self.canvas.get_height())).convert()

    @property
    def canvas_h(self):
        return self.canvas.get_height()
    @canvas_h.setter
    def canvas_h(self, val):
        self.canvas = pygame.Surface((self.canvas.get_width(), val)).convert()

    def ondrag(self, rel):
        size = self.canvas_w, self.canvas_h
        for i in (0, 1): # x, y
            self.drag_offset[i] = self.drag_offset[i] + rel[i]
            if self.drag_offset[i] > 0:
                self.drag_offset[i] = 0
            if self.drag_offset[i] < - size[i] + self.rect.size[i]:
                self.drag_offset[i] = - size[i] + self.rect.size[i];

