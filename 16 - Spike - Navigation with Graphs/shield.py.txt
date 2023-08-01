from vector2d import Vector2D
from point2d import Point2D
from graphics import egi, KEY
from math import sin,cos,radians
from random import random,randrange

class Shield(object):
    """Spawns randomly on the map and adds a shield to the enemy if picked up"""
    def __init__(self, world=None, enemy=None, scale=30.0):

        self.world = world
        self.enemy = enemy
        self.color = 'YELLOW'
        self.pos = Vector2D(randrange(0, world.cx), randrange(0, world.cy))
        dir = radians(random()*360)
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size

        self.shape = [
            Point2D(-1.0,  0.6),
            Point2D( 1.0,  0.0),
            Point2D(-1.0, -0.6)
        ]

        self.shield_value = 100
        self.cooldown = 10  # cooldown in seconds
        self.respawn_timer = None
        
        self.picked_up = False 

    def update(self, delta):
        if self.enemy:
            self.pos = self.enemy.pos
            self.heading = self.enemy.heading
            self.side = self.enemy.side

        if self.respawn_timer is not None:
            self.respawn_timer += delta
            if self.respawn_timer >= self.cooldown:
                self.pos = Vector2D(randrange(0, self.world.cx), randrange(0, self.world.cy))
                self.respawn_timer = None

    def render(self):
        '''Renders shield to screen'''
        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.shape, self.pos, self.heading, self.side, self.scale)
        egi.closed_shape(pts)

    def reset_position(self):
        self.pos = Vector2D(-100, -100)  # Move the shield object off-screen
        self.respawn_timer = 0  # Set the timer to 0
        self.picked_up = False
