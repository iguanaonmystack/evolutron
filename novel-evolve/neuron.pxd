from sprite cimport Sprite

cdef class Neuron(Sprite):
    cdef public object fn
    cdef public double raw_value
    cdef public double value
    cdef public double[:] input_weights
    
    cdef object font
    cdef object viewport
