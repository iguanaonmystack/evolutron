cimport sprite

cdef inline double double_min(double a, double b):
    return a if a < b else b

cdef inline double double_max(double a, double b):
    return a if a > b else b

cdef class Brain:
    cdef public object input_weights
    cdef public object output_weights
    cdef public object inputs
    cdef public object hidden0
    cdef public object outputs

    cdef object process(self, double[:] inputs)
    cpdef object reprocess(self)

cdef class Character(sprite.Sprite):
    cdef public object world
    cdef public object genome

    cdef public int haptic
    cdef public double vision_left
    cdef public double vision_right
    cdef int _vision_start_x, _vision_start_y
    cdef int _vision_left_end_x, _vision_left_end_y
    cdef int _vision_middle_end_x, _vision_middle_end_y
    cdef int _vision_right_end_x, _vision_right_end_y
    cdef public double on_water
    cdef public double on_grass
    cdef public double on_mulch

    cdef public int r
    cdef public double hue
    cdef public double predator
    cdef readonly double midx
    cdef readonly double midy
    cdef public double height
    cdef public int created
    cdef public object tile

    cdef public double angle
    cdef public double speed
    cdef public double spawn
    cdef public int spawn_refractory

    cdef public float energy
    cdef public int age
    cdef public int gen
    cdef public int parents
    cdef public int children

    cdef public Brain brain

    cdef public bint redraw

    cdef inline void interactions(self, group)
    cdef void load_genome(Character self, object genome)
    cdef void _draw_border(self, colour)
    cpdef void set_midpoint_x(self, double x)
    cpdef void set_midpoint_y(self, double y)
    cpdef void die(self)
    cpdef void spawn_asex(self)
