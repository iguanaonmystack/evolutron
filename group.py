from pygame.sprite import Group as pygame_Group

class Group(pygame_Group):
    def draw(self, onto, *args, **kw):
        for sprite in self:
            sprite.draw(*args, **kw)
        super(Group, self).draw(onto)
