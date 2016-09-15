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


__version__ = '$Id: stress-test.py v0.0.2$'
__author__ = 'Gummbum, (c) 2011-2012'


import time, random
import pygame
from pygame.locals import *
import gameclock
from gameclock import GameClock


SIM_LOAD = True
DEBUG = True

pygame_time = pygame.time.get_ticks


class Game(object):
    
    def __init__(self):
        self.screen = pygame.display.set_mode((800,600))
        self.screen_rect = self.screen.get_rect()
        self.font = pygame.font.SysFont(None, 16)
        self.clock = GameClock(
            30, 120,
            update_callback=self.update,
            frame_callback=self.draw,
            paused_callback=self.pause,
        )
        self.draw_line = pygame.draw.line
        self.ucolor = Color('grey')
        self.dcolor = Color('white')
        self.pcolor = Color('blue')
        self.running = True
        self.paused = False
        
        self.ball = pygame.Surface((30,30))
        self.ball.fill(Color(255,0,0))
        self.ball_start = 300
        self.ball_rect = self.ball.get_rect(x=self.ball_start)
        self.ball_from = self.ball_start
        self.ball_to = self.ball_start
        
        self.elapsed = 0.
        self.nupdates = 0
        self.n10updates = 0
        self.utime = pygame_time()
        self.dtime = pygame_time()
        self.ptime = pygame_time()
        self.uerror = 0
        self.derror = 0
        self.umax = 0
        self.dmax = 0
        self.ptxt = None
        self.msgs = []
        
        # Recur every second
        self.clock.schedule_interval(self.per_second, 1.)
        # Recur every 10 seconds
        self.clock.schedule_interval(self.per_10_second, 10.)
        # Recur every second, for two iterations
        self.clock.schedule_interval(self.recur, 1., 2)
    
    def run(self):
        clock = self.clock
        while self.running:
            clock.tick()
    
    def update(self, dt):
        # Track accuracy. For example, at 30 ups, each update+frames set
        # should not exceed 33 ms.
        t = pygame_time()
        utime = self.utime
        mydt = (t - utime)/1000.
        self.uerror += dt - mydt
        self.utime = t
        
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                self.on_key_down(e)
        
        self.ball_from = self.ball_to
        self.ball_to += dt * 200
        
        ## waste many ms / update
        if SIM_LOAD:
            pygame.time.wait(self.umax)
    
    def draw(self, interp):
        t = pygame_time()
        #
        self.screen.fill((0,0,0))
        x = self.screen_rect.centerx
        
        y = 10
        error = min(max(self.uerror/1000,-100),100)
        self.draw_line(self.screen, self.ucolor, (x,y), (x+error,y), 5)
        
        y += 10
        txt = self.font.render('DT Update ms error: {0:+0.3f}'.format(self.uerror), True, self.ucolor)
        r = txt.get_rect(centerx=x,top=y)
        self.screen.blit(txt, r)
        
        y += 20
        self.ball_rect.y = y
        dx = (self.ball_to - self.ball_from) * self.clock.interpolate
        self.ball_rect.centerx = self.ball_from + dx
        self.screen.blit(self.ball, self.ball_rect)
        
        for i,msg in enumerate(self.msgs):
            r = msg.get_rect(x=3)
            r.y = 3 + (3+r.h) * i
            self.screen.blit(msg, r)
        
        pygame.display.flip()
        
        ## waste many ms / frame
        if SIM_LOAD:
            pygame.time.wait(self.dmax)
    
    def pause(self):
        for e in pygame.event.get():
            if e.type == KEYDOWN:
                self.on_key_down(e)
        msg = 'Time is PAUSED' if self.paused else 'Time is Running'
        self.msgs[0] = self.font.render(msg, True, Color('grey'))
        self.draw(self.clock.interpolate)
    
    def per_second(self, *args):
        # flip the ball and performance meter every second
        self.nupdates += 1
        del self.msgs[:]
        for msg in (
            'Time is PAUSED' if self.paused else 'Time is Running',
            '{0:d} second elapsed'.format(self.nupdates),
            '{0:d} 10-second elapsed'.format(self.n10updates),
            '{0:.1f} / {1:.1f} ups/max'.format(self.clock.ups, self.clock.max_ups),
            '{0:.1f} / {1:.1f} fps/max'.format(self.clock.fps, self.clock.max_fps),
            '{0:d} update waste ms'.format(self.umax),
            '{0:d} draw waste ms'.format(self.dmax),
            '{0:d} use wait'.format(self.clock.use_wait),
            '{0:f} DT update'.format(self.clock.dt_update),
            '{0:f} cost of update'.format(self.clock.cost_of_update),
            '{0:f} DT frame'.format(self.clock.dt_frame),
            '{0:f} cost of frame'.format(self.clock.cost_of_frame),
        ):
            self.msgs.append(self.font.render(msg, True, Color('grey')))
        self.ball_from = self.ball_start
        self.ball_to = self.ball_from + self.clock.dt_update * 200
    
    def per_10_second(self, *args):
        self.n10updates += 10
        msg = '{0:d} 10-second elapsed'.format(self.n10updates)
        self.msgs[2] = self.font.render(msg, True, Color('grey'))
    
    def recur(self, *args):
        print 'RECUR'
    
    def on_key_down(self, e):
        if e.key == K_SPACE:
            # toggle max FPS: 0 vs. 60
            self.clock.max_fps = 0 if self.clock.max_fps else 120
            if DEBUG: print '\n--- max_fps:{0:d} ---'.format(self.clock.max_fps)
        elif e.key == K_UP:
            if e.mod & KMOD_SHIFT:
                # increment simulated update load
                self.umax += 5
                if DEBUG: print '\n--- umax +5:{0:d} ---'.format(self.umax)
            else:
                # increment simulated draw load
                self.dmax += 5
                if DEBUG: print '\n--- dmax +5:{0:d} ---'.format(self.dmax)
        elif e.key == K_DOWN:
            if e.mod & KMOD_SHIFT and self.umax:
                # decrement simulated update load
                self.umax -= 5
                if DEBUG: print '\n--- umax -5:{0:d} ---'.format(self.umax)
            elif self.dmax:
                # decrement simulated draw load
                self.dmax -= 5
                if DEBUG: print '\n--- dmax -5:{0:d} ---'.format(self.dmax)
        elif e.key == K_d:
            # toggle debug messages
            gameclock.DEBUG = not gameclock.DEBUG
            if gameclock.DEBUG:
                print '\n--- debug on ---'
            else:
                print '\n--- debug off ---'
        elif e.key == K_p:
            if self.paused:
                # pause clock
                self.paused = False
                self.clock.resume()
            else:
                # unpause clock
                self.paused = True
                self.clock.pause()
        elif e.key == K_w:
            # toggle use_wait
            self.clock.use_wait = not self.clock.use_wait
            if self.clock.use_wait:
                if DEBUG: print '\n--- wait on---'
            else:
                if DEBUG: print '\n--- wait off ---'
        elif e.key == K_ESCAPE:
            quit()


pygame.init()
Game().run()
