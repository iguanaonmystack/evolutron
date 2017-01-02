
import pygame
from pygame.locals import *


class TextBox(pygame.sprite.Sprite):

    def __init__(self, parent, rect):
        super(TextBox, self).__init__()

        self.parent = parent

        self.image = pygame.Surface((rect.w, rect.h)).convert()
        self.rect = rect

        self.font = pygame.font.SysFont('DejaVuSansMono,FreeMono,Monospace', 12)
        self.value = ''

        self.callback = None

    def _draw_border(self, colour):
        pygame.draw.lines(self.image, colour, 1, [
            (0, 0), (self.rect.w - 1, 0), (self.rect.w - 1, self.rect.h - 1), (0, self.rect.h - 1)
        ], 3)

    def draw(self):
        self.image.fill((0, 0, 0))
        if self.parent.focus == self:
            self._draw_border((255, 255, 255))
        else:
            self._draw_border((128, 128, 128))
        text = self.font.render(self.value, True, (255, 255, 255))
        self.image.blit(text, (2, 2))
    
    def onclick(self, pos, button):
        pass

    def onevent(self, event):
        if event.type == KEYDOWN:
            if event.key == K_BACKSPACE:
                self.value = self.value[:-1]
            elif event.key == K_ESCAPE:
                self.parent.focus = None
            elif event.key == K_RETURN:
                self.parent.focus = None
            else:
                self.value += pygame.key.name(event.key)
            if self.callback:
                self.callback()
        return False # don't propagate

