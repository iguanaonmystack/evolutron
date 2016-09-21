#!/usr/bin/env python

# This file is part of GameClock.
#
# GameClock is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GameClock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with GameClock.  If not, see <http://www.gnu.org/licenses/>.


__version__ = '$Id: demo.py v0.0.2$'
__author__ = 'Gummbum, (c) 2011-2012'


__doc__ = """
Keyboard controls:
    C       Clear (toggle screen.fill, balls can leave a trail)
    I       Interpolation
    L       Logic (swap clocks)
    P       Pause
    W       Wait
    TAB     Cycle GameClock settings profile
    +/=     Add 25 balls
    -       Remove half the balls
    UP      Increase ball speed by 2.5; Max 30
    DOWN    Decrease ball speed by 2.5; Min 2.5
    EACAPE  Quit
"""

import gc
import random
import time

import pygame
from pygame.locals import *

from gameclock import GameClock


class Settings:
    resolution = 800,600
    
    num_balls = 100
    ball_speed = 20.0
    
    max_ups = 30
    use_interpolation = False
    
    screen_rect = None
    
    # Invoke garbage collection when there are this many objects to collect.
    # The elements correspond to the generation.
    gc_min_collect = (50,25,25)


class Ball(object):
    
    size = (40,40)
    image = None
    color = None
    
    def __init__(self, screen_rect):
        self.rect = Rect(0,0,*self.size)
        if not self.image:
            self.image = pygame.surface.Surface(self.size)
            self._detail_block()
        self.step_rect = self.rect.copy()
        w,h = screen_rect.size
        self.x = float(random.randrange(self.size[0],w-self.size[0]))
        self.y = float(random.randrange(self.size[1],h-self.size[1]))
        self.x_prev = self.x
        self.y_prev = self.y
        self.rect.center = round(self.x),round(self.y)
        self.dx = random.choice([-1,1])
        self.dy = random.choice([-1,1])
    
    def _dim(self, color, frac):
        # Dim a color by factor frac
        c = Color(*color)
        c.r = int(round(c.r*frac))
        c.g = int(round(c.g*frac))
        c.b = int(round(c.b*frac))
        return c
    
    def _detail_block(self):
        # Render a block surface's detail
        image = self.image
        rect = self.rect
        color = self.color = Color('red')
        image.fill(self._dim(color,0.6))
        tl,tr = (0,0),(rect.width-1,0)
        bl,br = (0,rect.height-1),(rect.width-1,rect.height-1)
        pygame.draw.lines(image, color, False, (bl,tl,tr))
        pygame.draw.lines(image, self._dim(color,0.3), False, (tr,br,bl))
    
    def update(self, dt):
        """Call once per tick to update state."""
        x = self.x
        y = self.y
        dx = self.dx
        dy = self.dy
        self.x_prev = x
        self.y_prev = y
        x += dx * Settings.ball_speed
        y += dy * Settings.ball_speed
        step_rect = self.step_rect
        step_rect.topleft = round(x),round(y)
        screen_rect = Settings.screen_rect
        if not screen_rect.contains(step_rect):
            # rebound off edge
            (tl,tt),(tr,tb) = step_rect.topleft,step_rect.bottomright
            (sl,st),(sr,sb) = screen_rect.topleft,screen_rect.bottomright
            if tr > sr:
                # dx is positive, right edge too far
                over = sr - tr  # negative
                x += over
                dx = -dx
            elif tl < sl:
                # dx is negative, left edge too far
                under = sl + tl  # positive
                x -= under
                dx = -dx
            if tb > sb:
                # dy is positive, bottom edge too far
                over = sb - tb  # negative
                y += over
                dy = -dy
            elif tt < st:
                # dy is negative, top edge too far
                under = st + tt  # positive
                y -= under
                dy = -dy
            self.dx = dx
            self.dy = dy
            step_rect.topleft = round(x),round(y)
        self.x = x
        self.y = y
        self.rect.topleft = self.step_rect.topleft


class Clock(object):
    """a clock class that can switch its internal clock"""
    
    def __init__(self, update_callback, frame_callback, paused_callback):
        
        # Setting up the clocks
        
        # Game clock settings profiles
        self.gameclock_limits = (
            # MaxUPS, MaxFPS
            (30, 0),   # unlimited FPS
            (30, 60),  # max FPS is double UPS
            (30, 120), # max FPS is quadruple UPS
            (30, 30),  # max FPS is UPS
            (6, 0),    # UPS is 6; unlimited FPS
        )
        self.gameclock_settings = 0
        
        # Make the clocks
        max_ups,max_fps = self.gameclock_limits[self.gameclock_settings]
        self.clocks = {
            'pygame' : pygame.time.Clock(),
            'gameclock' : GameClock(
                max_ups=max_ups,
                max_fps=max_fps,
                use_wait=False,
                update_callback=update_callback,
                frame_callback=frame_callback,
                paused_callback=paused_callback),
        }
        
        # Extras for when pygame clock is swapped in
        self.update_callback = update_callback
        self.frame_callback = frame_callback
        self.paused_callback = paused_callback
        self.paused = False
        
        # The clock that is active
        self.which_clock = 'gameclock'
        self.clock = None
        self.set_clock(self.which_clock)
    
    def tick(self):
        if self.which_clock == 'pygame':
            # pygame logic
            self.clock.tick(Settings.max_ups)
            if self.paused:
                self.paused_callback()
            else:
                self.update_callback()
                self.frame_callback()
        else:
            # GameClock logic
            self.clock.tick()
    
    def get_fps(self):
        if self.which_clock == 'pygame':
            return self.clock.get_fps(),Settings.max_ups
        else:
            return self.clock.fps,self.clock.max_fps
    
    def get_ups(self):
        if self.which_clock == 'pygame':
            return Settings.max_ups,Settings.max_ups
        else:
            return self.clock.ups,self.clock.max_ups
    
    @property
    def use_wait(self):
        return self.clocks['gameclock'].use_wait
    @use_wait.setter
    def use_wait(self, bool):
        self.clocks['gameclock'].use_wait = bool
    
    def pause(self):
        if self.paused:
            self.clocks['gameclock'].resume()
            self.paused = False
        else:
            self.clocks['gameclock'].pause()
            self.paused = True
    
    def set_clock(self, which):
        if which not in self.clocks:
            raise pygame.error,'invalid clock: {0}'.format(which)
        self.which_clock = which
        self.clock = self.clocks[which]
    
    def next_gameclock_settings(self):
        self.gameclock_settings += 1
        if self.gameclock_settings >= len(self.gameclock_limits):
            self.gameclock_settings = 0
        
        max_ups,max_fps = self.gameclock_limits[self.gameclock_settings]
        clock = self.clocks['gameclock']
        clock.max_ups = max_ups
        clock.max_fps = max_fps
        Settings.max_ups = max_ups


class Game(object):
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(Settings.resolution)
        self.bgcolor = Color(175,125,125)
        self.screen.fill(self.bgcolor)
        self.screen_rect = self.screen.get_rect()
        Settings.screen_rect = self.screen_rect
        self.clear_screen = True
        #
        self.clock = Clock(self.update, self.draw, self.pause)
        #
        self.balls = [
            Ball(self.screen_rect) for i in range(Settings.num_balls)]
        # A timer for stats. GameClock could do this for us if we were not
        # swapping between GameClock and pygame Clock.
        self.font = pygame.font.SysFont(None, 16)
        self.msgs = []
        self.elapsed = 0.0
    
    def run(self):
        self.game_is_running = True
        while self.game_is_running:
            self.clock.tick()
    
    def update(self, dt=1000.0/30.0):
        #
        self.update_events()
        for ball in self.balls:
            ball.update(dt)
        # A timer for stats. GameClock could do this for us if we were not
        # swapping between GameClock and pygame Clock.
        self.elapsed += dt
        if self.elapsed >= 1.0:
            self.elapsed -= 1.0
            self.update_stats()
        
        # Garbage collection. This combats jerkiness, especially visible
        # when interpolation is on. Gentle warning: this may not be
        # CPU-friendly for some workloads. But it seems to be okay for
        # this demo's workload.
        for i,n in enumerate(gc.get_count()):
            if n > Settings.gc_min_collect[i]:
                gc.collect(i)
    
    def update_stats(self):
        del self.msgs[:]
        if self.clock.which_clock == 'pygame':
            for msg in (
                'L: {0}'.format('pygame' if self.clock.which_clock=='pygame' else 'GameClock'),
                '{0:.1f} / {1:.1f} ups/max'.format(*self.clock.get_ups()),
                '{0:.1f} / {1:.1f} fps/max'.format(*self.clock.get_fps()),
                '+/-: Balls {0:d}'.format(len(self.balls)),
                'UP/DOWN: Ball speed {0:0.1f}'.format(Settings.ball_speed),
            ):
                self.msgs.append(self.font.render(msg, True, Color('grey')))
        else:
            for msg in (
                'L: {0}'.format('pygame' if self.clock.which_clock=='pygame' else 'GameClock'),
                'TAB: {0:.1f} / {1:.1f} ups/max'.format(*self.clock.get_ups()),
                'TAB: {0:.1f} / {1:.1f} fps/max'.format(*self.clock.get_fps()),
                'I: Interpolation {0}'.format('ON' if Settings.use_interpolation else 'OFF'),
                'W: Use wait {0}'.format('ON' if self.clock.use_wait else 'OFF'),
                '+/-: Balls {0:d}'.format(len(self.balls)),
                'UP/DOWN: Ball speed {0:0.1f}'.format(Settings.ball_speed),
            ):
                self.msgs.append(self.font.render(msg, True, Color('grey')))
    
    def update_events(self):
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                self.do_key_down(e.unicode, e.key, e.mod)
            elif e.type == QUIT:
                self.do_quit()
    
    def do_key_down(self, unicode, key, mod):
        if key == K_c:
            # Toggle screen.fill.
            self.clear_screen = not self.clear_screen
        elif key == K_i:
            # Toggle interpolation.
            Settings.use_interpolation = not Settings.use_interpolation
        elif key == K_l:
            # Swap clocks.
            if self.clock.which_clock == 'pygame':
                self.clock.set_clock('gameclock')
            else:
                self.clock.set_clock('pygame')
        elif key == K_p:
            # Toggle pause.
            self.clock.pause()
        elif key == K_w:
            # Toggle wait.
            self.clock.use_wait = not self.clock.use_wait
        elif key == K_TAB:
            # Cycle GameClock settings profile.
            self.clock.next_gameclock_settings()
        elif key in (K_PLUS,K_EQUALS):
            # Add 25 balls.
            for i in range(25):
                self.balls.append(Ball(self.screen_rect))
        elif key == K_MINUS:
            # Remove half the balls.
            if len(self.balls) >= 2:
                for i in range(len(self.balls)/2):
                    self.balls.pop(0)
        elif key == K_UP:
            # Increase ball speed by 2.5. Max 30.
            if Settings.ball_speed < 30.0:
                Settings.ball_speed += 2.5
        elif key == K_DOWN:
            # Decrease ball speed by 2.5. Min 2.5.
            if Settings.ball_speed > 2.5:
                Settings.ball_speed -= 2.5
        elif key == K_ESCAPE:
            # Quit.
            quit()
    
    def do_quit(self):
        quit()
    
    def draw(self, interp=1.0):
        screen = self.screen
        blit = screen.blit
        if self.clear_screen:
            screen.fill(self.bgcolor)
        for ball in self.balls:
            if Settings.use_interpolation:
                x,y = ball.x_prev,ball.y_prev
                dx = (ball.x - x) * interp
                dy = (ball.y - y) * interp
                x,y = round(x+dx),round(y+dy)
            else:
                x,y = ball.rect.topleft
            blit(ball.image, (x,y))
        for i,msg in enumerate(self.msgs):
            y = i * (msg.get_height() + 2)
            blit(msg, (3,y))
        pygame.display.flip()
    
    def pause(self, *args):
        pygame.time.wait(10)
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                if e.key == K_p:
                    self.clock.pause()

if __name__ == '__main__':
    gc.disable()
    Game().run()
