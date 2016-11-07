# cython: profile=True

import operator
from itertools import combinations
from pygame.sprite import Group as pygame_Group, collide_rect, spritecollideany

from characters import Character
from genome import Genome

class Group(pygame_Group):
    def __init__(self, world=None):
        super(Group, self).__init__()
        self.world = world

    def draw(self, onto, offset=(0,0)):
        for sprite in self.spritedict:
            sprite.draw()
        # Group.draw() basically just does [onto.blit(s.image, s.rect) for s...]
        super(Group, self).draw(onto)

    def collisions(self):
        world = self.world
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

                # sexual reproduction:
                if sprite.spawn > 0 and other.spawn > 0 \
                and sprite.energy > 3000 and other.energy > 3000:
                    sprite.energy -= 3000
                    other.energy -= 3000
                    newgenome = Genome.from_parents(sprite.genome, other.genome)
                    newchar = Character.from_genome(world, newgenome)
                    newchar.x = sprite._x + other._x // 2
                    newchar.y = sprite._y + other._y // 2
                    newchar.gen = max(sprite.gen, other.gen) + 1
                    newchar.parents = 2
                    sprite.children += 1
                    other.children += 1
                    op = operator.sub
                    while spritecollideany(newchar, world.allcharacters):
                        newchar.x = op(newchar.x, 1)
                        if newchar.x < 1:
                            op = operator.add
                    world.allcharacters.add(newchar)


