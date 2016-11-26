import pyximport; pyximport.install()

import os
import sys
import time
import json
import argparse

import random
random.seed(101)

import pygame
from pygame.locals import *

import tiles
import characters
import window as _window

def main():
    parser = argparse.ArgumentParser(description='An evolution simulator')
    parser.add_argument(
        '--screenshot', dest='screenshot', metavar='f', action='store',
        default=False,
        help='Take a screenshot, save to given filename, and exit')
    parser.add_argument(
        '--profile', dest='profile', action='store_true', default=False,
        help='Run headless for 1000 ticks to get profile data')
    parser.add_argument(
        '-f', '--fullscreen', dest='fullscreen', action='store_true',
        default=False,
        help='Run full-screen')
    parser.add_argument(
        '--inspect', metavar='f', dest='inspect', action='store', default=None,
        help='Run inspector for the given file')
    args = parser.parse_args()

    if args.screenshot:
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    pygame.mixer.quit() # Pygame's sound causes static on my computer.

    if args.inspect:
        import inspectmain
        return inspectmain.main(args)
    
    flags = 0 #RESIZABLE
    if args.fullscreen:
        print('running full screen')
        flags = FULLSCREEN
    screen = pygame.display.set_mode((1280, 720), flags, 32)
    window = _window.Window(screen, 2000, 2000)

    mousedown_pos = None
    mouse_was_dragged = False

    if args.screenshot or args.profile:
        os.putenv('SDL_VIDEODRIVER', 'fbcon')
        pygame.display.init()

    if args.screenshot:
        for i in range(10):
            window.update()
        window.frame()
        pygame.image.save(window.screen, args.screenshot)
        return
    
    if args.profile:
        for i in range(1000):
            window.update()
        return

    tickrate = 1/60.  # target maximum
    framerate = 1/60. # will never be faster than tick rate
    last_t = t = time.perf_counter() # py3.3 +
    last_frame = time.perf_counter()
    render = True
    pause = False
    while 1:
        last_t = t
        t = time.perf_counter()
        time_passed = t - last_t
        #print('sleeping', tickrate - time_passed)
        time.sleep(max(0, tickrate - time_passed))
        
        if not pause:
            t1 = time.perf_counter()
            window.update()
            t2 = time.perf_counter()
            print('tick time', t2 - t1, 'target tickrate', tickrate)

        if t - last_frame > framerate and render:
            print('frame time', t - last_frame)
            window.frame()
            last_frame = t

        for event in pygame.event.get():
            if event.type == QUIT:
                return
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE or event.key == K_q:
                    return
                elif event.key == K_p:
                    if pause:
                        pause = False
                    else:
                        pause = True
                elif event.key == K_r:
                    if render:
                        render = False
                    else:
                        render = True
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
