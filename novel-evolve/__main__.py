import os
import sys
import time
import json
import argparse

import random
random.seed(100)

import pygame
from pygame.locals import *

import gameclock

import tiles
import characters
import window as _window

def main():
    parser = argparse.ArgumentParser(description='An evolution simulator')
    parser.add_argument(
        '--screenshot', dest='screenshot', action='store', default=False,
        help='Take a screenshot and exit')
    args = parser.parse_args()

    if args.screenshot:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()

    screen = pygame.display.set_mode((1000, 1000), RESIZABLE, 32)
    window = _window.Window(screen, 2000, 2000)

    mousedown_pos = None
    mouse_was_dragged = False

    if args.screenshot:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        pygame.display.init()
        window.update(1)
        window.update(1)
        window.frame(0)
        pygame.image.save(window.screen, args.screenshot)
        return

    clock = gameclock.GameClock(
        max_ups=60,     # game running speed
        max_fps=60,     # supposed max fps
        use_wait=True,
        update_callback=window.update,
        frame_callback=window.frame,
        paused_callback=None)

    while 1:
        clock.tick()

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return
                elif event.key == K_p:
                    if clock.update_callback is None:
                        clock.update_callback = window.update
                    else:
                        clock.update_callback = None
                elif event.key == K_r:
                    if clock.frame_callback is None:
                        clock.frame_callback = window.frame
                    else:
                        clock.frame_callback = None
                elif event.key == K_d:
                    if window.world.active_item:
                        with open('active-%s.json'%int(time.time()), 'w') as f:
                            json.dump(window.world.active_item.dump(), f,
                                sort_keys=True, indent=4)
            elif event.type==VIDEORESIZE:
                screen = pygame.display.set_mode(event.dict['size'], RESIZABLE)
                window.screen = screen
                window.onresize(*event.dict['size'])
            elif event.type == MOUSEBUTTONDOWN:
                mousedown_pos = event.dict['pos']
                mouse_was_dragged = False
            elif event.type == MOUSEBUTTONUP:
                mousedown_pos = None
                button = event.dict['button'] #1/2/3=left/middle/right, 4/5=wheel
                if not mouse_was_dragged:
                    window.onclick(event.dict['pos'], button)
            elif event.type == MOUSEMOTION and mousedown_pos is not None:
                mouse_was_dragged = True
                window.ondrag(mousedown_pos, event.dict['rel'])


if __name__ == '__main__':
    main()
