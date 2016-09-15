import pygame
from pygame.locals import *



class Character(pygame.sprite.Sprite):
    def __init__(self, world):
        super(Character, self).__init__()
        
        self.world = world

        self.r = 25
        self.image = pygame.Surface((self.r * 2, self.r * 2), SRCALPHA).convert_alpha()
        self.rect = self.image.get_rect()

        self._x = None
        self._y = None
        self.acc_x = 0
        self.acc_y = 0

    @property
    def colour(self):
        pass

    @colour.setter
    def colour(self, color):
       self.image.fill(color)
    
    def update(self):
        self.x += self.acc_x
        self.y += self.acc_y
        collided = pygame.sprite.spritecollide(self, self.world.allcharacters, 0)
        collided += pygame.sprite.spritecollide(self, self.world.allwalls, 0)
        for item in collided:
            if item is not self:
                self.x -= self.acc_x
                self.y -= self.acc_y
                self.acc_x = 0 #-self.acc_x
                self.acc_y = 0 #-self.acc_y

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

