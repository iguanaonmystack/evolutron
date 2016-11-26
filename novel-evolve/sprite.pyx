from sprite cimport Sprite

cdef class Sprite:
    def __init__(self):
        self.__g = {}

    def add_internal(self, group):
        self.__g[group] = 0

    def remove_internal(self, group):
        del self.__g[group]

