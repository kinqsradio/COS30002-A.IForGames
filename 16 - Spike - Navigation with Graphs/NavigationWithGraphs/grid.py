from graphics import egi
from point2d import Point2D
from vector2d import Vector2D
from math import floor
from random import randrange
import heapq
from block import *

class Grid(object):
    def __init__(self, world):
        self.world = world
        self.scale = 50
        self.grid_size = world.cx / world.cy * self.scale
        self.height = round(world.cx / self.grid_size)
        self.width = round(world.cy / self.grid_size)
        self.grid = [[0 for x in range(self.width)] for y in range(self.height)]

    def render(self):
        grid = self.grid_size
        egi.white_pen()
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                pt1 = Point2D(i * grid, j * grid)
                pt2 = Point2D(pt1.x + grid, pt1.y)
                pt3 = Point2D(pt1.x, pt1.y + grid)
                egi.line_by_pos(pt1, pt2)
                egi.line_by_pos(pt1, pt3)

    def get_node(self, pt):
        if pt is None:
            return None
        
        i = floor(pt.x / self.grid_size)
        j = floor(pt.y / self.grid_size)

        if 0 <= i < len(self.grid) and 0 <= j < len(self.grid[i]):
            return Vector2D(i, j)



    def fit_pos(self, pt, type):
        i = floor(pt.x / self.grid_size)
        j = floor(pt.y / self.grid_size)

        if type == 'center':
            return Vector2D(i * self.grid_size + self.grid_size / 2, j * self.grid_size + self.grid_size / 2)
        elif type == 'corner':
            return Vector2D(i * self.grid_size, j * self.grid_size)

    def get_pos(self, pt, type):
        return self.fit_pos(Point2D(pt.x * self.grid_size, pt.y * self.grid_size), type)

    def node_available(self, node):
        return not self.grid[node.x][node.y]

    def node_exists(self, pt):
        return pt.x in range(0, self.width) and pt.y in range(0, self.height)

    def update_grid(self, node):
        self.grid[node.x][node.y] = 1


