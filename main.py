import sys
import random
random.seed(100)

import pygame
from pygame.locals import *

import tiles
import characters
import world as _world

def main():
    pygame.init()

    viewport_size = (1000, 1000)
    screen = pygame.display.set_mode(viewport_size, pygame.RESIZABLE)
    pygame.display.set_caption('Window Title!')
    w, h = pygame.display.get_surface().get_size()

    # We shouldn't actually see the background, but have a nice grey for it.
    world_size = (2000,2000)
    background = pygame.Surface(world_size)
    background = background.convert()
    background.fill((128,128,128))

    world = _world.World(*world_size + (background,))
    mousedown_pos = None
    viewport_offset = [0, 0]

    clock = pygame.time.Clock()
    while 1:
        clock.tick(60) #fps

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return
            elif event.type==VIDEORESIZE:
                viewport_size = event.dict['size']
                screen = pygame.display.set_mode(
                        viewport_size, RESIZABLE)
                background = pygame.Surface(screen.get_size()).convert()
                background.fill((128, 128, 128))
                world.background = background
            elif event.type == MOUSEBUTTONDOWN:
                mousedown_pos = event.dict['pos']
            elif event.type == MOUSEBUTTONUP:
                mousedown_pos = None
            elif event.type == MOUSEMOTION and mousedown_pos is not None:
                rel = event.dict['rel']
                for i in (0, 1):
                    viewport_offset[i] = viewport_offset[i] + rel[i]
                    if viewport_offset[i] > 0:
                        viewport_offset[i] = 0
                    if viewport_offset[i] < - world_size[i] + viewport_size[i]:
                        viewport_offset[i] = - world_size[i] + viewport_size[i];
        
        world.update()
        screen.blit(background, viewport_offset)
        pygame.display.flip()


if __name__ == '__main__':
    main()
