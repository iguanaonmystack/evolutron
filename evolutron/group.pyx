# cython: profile=True
cimport cython

import operator
from itertools import combinations
from pygame.sprite import Group as pygame_Group, collide_rect, spritecollideany

from characters cimport Character
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

    @cython.cdivision(True)
    def collisions(self):
        cdef double xoff, yoff
        cdef Character sprite, other, newchar, predator, prey
        world = self.world
        for sprite, other in combinations(self, 2):
            if collide_rect(sprite, other):
                sprite_midpoint_x = sprite.midx
                sprite_midpoint_y = sprite.midy
                other_midpoint_x = other.midx
                other_midpoint_y = other.midy
                midpoint_x = (sprite_midpoint_x + other_midpoint_x) / 2
                midpoint_y = (sprite_midpoint_y + other_midpoint_y) / 2

                sprite_move_x = 5. / (sprite_midpoint_x - midpoint_x)
                sprite_move_y = 5. / (sprite_midpoint_y - midpoint_y)
                sprite.set_midpoint_x(sprite_midpoint_x + min(sprite_move_x, 2.5))
                sprite.set_midpoint_y(sprite_midpoint_y + min(sprite_move_y, 2.5))
                other_move_x = 5. / (other_midpoint_x - midpoint_x)
                other_move_y = 5. / (other_midpoint_y - midpoint_y)
                other.set_midpoint_x(other_midpoint_x + min(other_move_x, 2.5))
                other.set_midpoint_y(other_midpoint_y + min(other_move_y, 2.5))

                sprite.haptic = 1
                sprite.speed /= 2
                other.haptic = 1
                other.speed /= 2

                if sprite.predator == other.predator:
                    # sexual reproduction:
                    if sprite.spawn > 0 and other.spawn > 0 \
                    and sprite.energy > 2500 and other.energy > 2500 \
                    and sprite.spawn_refractory == 0 and other.spawn_refractory == 0:
                        sprite.energy -= 2500
                        other.energy -= 2500
                        sprite.spawn_refractory = 30
                        other.spawn_refractory = 30
                        newgenome = Genome.from_parents(sprite.genome, other.genome)
                        newchar = Character(world)
                        newchar.load_genome(newgenome)
                        newchar.set_midpoint_x(midpoint_x)
                        newchar.set_midpoint_y(midpoint_y)
                        newchar.gen = max(sprite.gen, other.gen) + 1
                        newchar.parents = 2
                        newchar.energy = 4000
                        sprite.children += 1
                        other.children += 1
                        world.allcharacters.add(newchar)
                else:
                    # nom nom nom nom nom
                    if sprite.predator:
                        predator = sprite
                        prey = other
                    else:
                        predator = other
                        prey = sprite
                    
                    predator.foodchain = True
                    prey.foodchain = True
                    if prey.energy < 1000:
                        predator.energy += prey.energy
                        prey.energy = 0
                        prey.die()
                    else:
                        predator.energy += 900
                        prey.energy -= 1000

