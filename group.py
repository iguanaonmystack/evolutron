from pygame.sprite import Group as pygame_Group

class Group(pygame_Group):
    def draw(self, onto, offset=(0,0)):
        for sprite in self:
            sprite.draw()
        # Group.draw() basically just does [onto.blit(s.image, s.rect) for s...]
        super(Group, self).draw(onto)
