"""pygame-compatible sprite extension type"""

cdef class Sprite:
    cdef object __g
    cdef public object image
    cdef public object rect

