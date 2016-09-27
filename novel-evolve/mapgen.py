'''mapgen.py -- originally world.py in NaNoGenMo project.'''

import random
import operator
from collections import OrderedDict

class Map(list):
    def __init__(self, x, y):
        self.sizex = x
        self.sizey = y

    @classmethod
    def from_random(cls, x, y):
        self = cls(x, y)
        tiles = x * y

        # Generate blank grid:
        for i in range(x):
            row = []
            self.append(row)
            for j in range(y):
                row.append(None)

        # Generate some forests:
        for n in range(tiles // 16):
            sizex = random.randint(0, 5)
            sizey = random.randint(0, 5)
            origin = random.randint(0, x - sizex - 1), random.randint(0, y - sizey - 1)
            for i in range(origin[0], origin[0] + sizex):
                for j in range(origin[1], origin[1] + sizey):
                    self[i][j] = Tile(i, j, 'forest')

        # Generate some lakes:
        for n in range(tiles // 64):
            centre = random.randint(0, x - 1), random.randint(0, y - 1)
            radius = random.randint(0, 3)
            radius_sq = radius ** 2
            self[centre[0]][centre[1]] = Tile(centre[0], centre[1], 'lake')
            for offset_i in range(- radius, radius + 1):
                i = centre[0] + offset_i
                if i < 0 or i >= self.sizex:
                    continue
                offset_i_sq = offset_i ** 2
                for offset_j in range(- radius, radius + 1):
                    j = centre[1] + offset_j
                    if j < 0 or j >= self.sizey:
                        continue
                    offset_j_sq = offset_j ** 2
                    if offset_i_sq * offset_j_sq < radius_sq:
                        self[i][j] = Tile(i, j, 'lake')

        # Rest of the map is meadow:
        for i in range(x):
            for j in range(y):
                if self[i][j] is None:
                    self[i][j] = Tile(i, j, 'meadow')

        # Link up grid:
        for i in range(x):
            for j in range(y):
                tile = self[i][j]
                if j:
                    tile.south = self[i][j - 1]
                    self[i][j - 1].north = tile
                if i:
                    tile.west = self[i - 1][j]
                    self[i - 1][j].east = tile

        # unlink lakes so players can't walk out into them
        for i in range(x):
            for j in range(y):
                tile = self[i][j]
                if tile.terrain == 'lake':
                    for direction in ('north', 'south', 'east', 'west'):
                        neighbour = getattr(tile, direction)
                        if neighbour is None:
                            # edge of map
                            continue
                        if neighbour.terrain == 'lake':
                            setattr(tile, direction, None)
        return self
    
    def __str__(self):
        s = []
        for y in reversed(range(self.sizey)):
            s.append('    ')
            for x in range(self.sizex):
                s.append("%s | " % (self[x][y]))
            s.append('\n')
        return ''.join(s)


class Tile:
    def __init__(self, posx, posy, terrain):
        self.posx = posx
        self.posy = posy
        self.terrain = terrain
        self.west = None
        self.east = None
        self.north = None
        self.south = None

    def __str__(self):
        s = "%02s" % (self.terrain.symbol,)
        # s += '<' if self.west else ' '
        # s += '>' if self.east else ' '
        # s += '^' if self.north else ' '
        # s += 'v' if self.south else ' '
        return s

    def __repr__(self):
        return "<Tile at (%s, %s) terrain=%r>" % (self.posx, self.posy, self.terrain,)

    @property
    def neighbours(self):
        d = OrderedDict()
        for direction in ('north', 'east', 'south', 'west'):
            if getattr(self, direction) is not None:
                d[direction] = getattr(self, direction)
        return d

    def path_to(self, target_cls):
        """Determine the path to a terrain type or a prop type.
        
        Returns a tuple of (path, item), where:
        * path -- None if target not found, otherwise a list of
            (tile, direction)
        * item -- None if not found, otherwise the specific tile or prop found
        """
        visited_nodes = set()
        distances = {}
        parents = {}
        if issubclass(target_cls, terrains.Terrain):
            def target_fn(tile):
                return isinstance(tile, target_cls) and tile or None
        elif issubclass(target_cls, props.Prop):
            def target_fn(tile):
                for prop in tile.terrain.props:
                    if isinstance(prop, target_cls):
                        return prop
                return None
        else:
            raise RuntimeError('path_to() for unknown class %r' % (target_cls,))
        dest, item = _find(self, visited_nodes, distances, parents,
            target_fn=target_fn)
        if dest is not None:
            path = [(dest, '')]
            while path[0][0] != self:
                path = [parents[path[0][0]]] + path
            return path, item
        return None, None

    def recursive_update(self, action):
        visited_nodes = set()
        distances = {}
        parents = {}
        _find(self, visited_nodes, distances, parents,
            target_fn=None, action=action)

def _find(current, visited_nodes, distances, parents, target_fn=None, action=None):
    # Dijkstra's algorithm.
    item = target_fn and target_fn(current)
    if item is not None:
        return current, item
    for direction, neighbour in current.neighbours.items():
        if neighbour not in visited_nodes:
            dist = distances.setdefault(current, 0) + 1
            if neighbour in distances:
                if dist < distances[neighbour]:
                    distances[neighbour] = dist
                    parents[neighbour] = current, direction
            else:
                distances[neighbour] = dist
                parents[neighbour] = current, direction
    if action:
        action(current)
    visited_nodes.add(current)
    unvisited_distances = [
        (k, v) for k, v in distances.items() if k not in visited_nodes]
    if unvisited_distances:
        sorted_distances = sorted(
            unvisited_distances,
            key=operator.itemgetter(1))
        nearest_unvisited, dist = sorted_distances[0]
        return _find(nearest_unvisited, visited_nodes, distances, parents,
            target_fn=target_fn, action=action)
    else:
        # no unvisted nodes, unable to find target
        return None, None

def find(initial, target_fn=None):
    visited_nodes = set()
    distances = {}
    parents = {}
    dest, item = _find(initial, visited_nodes,
        distances, parents, target_fn=target_fn)
    if dest is not None:
        path = [(dest, '')]
        while path[0][0] != initial:
            path = [parents[path[0][0]]] + path
        return path, item
    return None, None

def opposite_direction(direction):
    d = {'north': 'south',
        'east': 'west',
        'south': 'north',
        'west': 'east'}
    return d[direction]


