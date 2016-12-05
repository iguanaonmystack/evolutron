'''inspectmain.py -- alternative main method for object inspector.'''
import json
import time
from functools import partial

import pygame
from pygame.locals import *

import group
import textbox
import infopane
import brainview
import characters

class InspectWindow(object):
    def __init__(self, screen, character):
        self.screen = screen

        self.allsprites = group.Group()
        
        self.brainview = brainview.BrainView(
            self, Rect(400, 0, 600, 1000), (200, 100))
        self.brainview.brain = character.brain
        self.allsprites.add(self.brainview)
        
        self.infopane = infopane.InfoPane(self, Rect(0, 0, 250, 1000))
        self.allsprites.add(self.infopane)

        for i, input_ in enumerate(character.brain.inputs):
            ypos = 25 + i * 100
            textbox_ = textbox.TextBox(self, Rect(275, ypos, 100, 25))
            self.allsprites.add(textbox_)
            def callback(textbox_, input_):
                try:
                    input_.value = float(textbox_.value)
                except ValueError:
                    pass
                character.brain.reprocess()
            textbox_.callback = partial(callback, textbox_, input_)

        self.focus = self.brainview

    def onevent(self, event):
        if self.focus and hasattr(self.focus, 'onevent'):
            if self.focus.onevent(event) is False:
                return
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE or event.key == K_q:
                pygame.event.post(pygame.event.Event(QUIT))

    def onclick(self, pos, button):
        for sprite in self.allsprites:
            if sprite.rect.collidepoint(pos):
                self.focus = sprite
                break
        else:
            self.focus = None

        if self.focus:
            if hasattr(self.focus, 'onclick'):
                relpos = pos[0] - self.focus.rect.x, pos[1] - self.focus.rect.y
                self.focus.onclick(relpos, button)


    def onresize(self, width, height):
        pass

    def ondrag(self, relpos, button):
        pass

    def update(self):
        pass
    
    def draw(self):
        self.infopane.text = self.brainview.active_item
        self.allsprites.draw(self.screen)
        pygame.display.flip()

def main(args):
    '''args -- parsed ArgumentParser Namespace from real main()'''
    savedata = json.load(open(args.inspect))
    print(savedata)
    character = characters.Character.load(savedata)

    screen = pygame.display.set_mode((1280, 720))
    window = InspectWindow(screen, character)

    mousedown_pos = None
    mouse_was_dragged = False

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
        time.sleep(max(0, tickrate - time_passed))
        
        if not pause:
            t1 = time.perf_counter()
            window.update()
            t2 = time.perf_counter()

        if t - last_frame > framerate and render:
            window.draw()
            last_frame = t

        for event in pygame.event.get():
            if event.type == QUIT:
                return
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
                mouse_was_dragged = False
            elif event.type == MOUSEMOTION and mousedown_pos is not None:
                mouse_was_dragged = True
                window.ondrag(mousedown_pos, event.dict['rel'])
            else:
                window.onevent(event)

