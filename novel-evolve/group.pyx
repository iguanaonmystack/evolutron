# cython: profile=True

from itertools import combinations
from pygame.sprite import Group as pygame_Group, collide_rect

class Group(pygame_Group):
    def draw(self, onto, offset=(0,0)):
        for sprite in self.spritedict:
            sprite.draw()
        # Group.draw() basically just does [onto.blit(s.image, s.rect) for s...]
        super(Group, self).draw(onto)

    def collisions(self):
        for sprite, other in combinations(self, 2):
            if collide_rect(sprite, other):
                if sprite.prev_x is not None:
                    sprite.x = sprite.prev_x
                    sprite.y = sprite.prev_y
                if other.prev_x is not None:
                    other.x = other.prev_x
                    other.y = other.prev_y
                # TODO - be smarter here. work out midpoint and use that.
                sprite.speed = 0
                sprite.haptic = 1
                other.speed = 0
                other.haptic = 1
