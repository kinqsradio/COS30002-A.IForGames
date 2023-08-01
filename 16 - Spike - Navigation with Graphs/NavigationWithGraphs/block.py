from vector2d import Vector2D
from matrix33 import Matrix33
from graphics import egi
from path import Path
from grid import *

class Block(object):
    def __init__(self, world, x, y):
        self.world = world
        self.pos = self.world.grid.fit_pos(Vector2D(x, y), 'corner')

    def render(self):
        cell_size = self.world.grid.grid_size
        egi.set_pen_color(name='RED')
        egi.rect(self.pos.x, self.pos.y, self.pos.x + cell_size, self.pos.y + cell_size, filled=True)
