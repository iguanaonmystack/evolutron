import sys
import random
random.seed(100)

import pygame
from pygame.locals import *

import gameclock

import tiles
import characters
import world as _world

def main():
    pygame.init()

    world_size = (2000,2000)
    world = _world.World(*world_size)

    mousedown_pos = None
    mouse_was_dragged = False

    clock = gameclock.GameClock(
        max_ups=60,     # game running speed
        max_fps=60,     # supposed max fps
        use_wait=True,
        update_callback=world.update,
        frame_callback=world.frame,
        paused_callback=None)
    while 1:
        clock.tick()

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return
            elif event.type==VIDEORESIZE:
                world.resize(*event.dict['size'])
            elif event.type == MOUSEBUTTONDOWN:
                mousedown_pos = event.dict['pos']
                mouse_was_dragged = False
            elif event.type == MOUSEBUTTONUP:
                mousedown_pos = None
                if not mouse_was_dragged:
                    world.onclick(event.dict['pos'])
            elif event.type == MOUSEMOTION and mousedown_pos is not None:
                mouse_was_dragged = True
                world.ondrag(event.dict['rel'])


if __name__ == '__main__':
    main()
