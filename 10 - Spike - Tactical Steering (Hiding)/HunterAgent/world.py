'''A 2d world that supports agents with steering behaviour

Created for COS30002 AI for Games by Clinton Woodward <cwoodward@swin.edu.au>

For class use only. Do not publically share or post this code without permission.

'''

import random
from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform
from path import Path
from agent import Agent
from matrix33 import Matrix33


class HideObject(object):
    def __init__(self, world=None, position=None, radius=5, color='WHITE'):
        self.world = world
        self.pos = position if position is not None else self.randomise_loc()
        self.radius = randrange(50, 70)
        self.color = color
        self.agents = []
        
    def update(self):
        self.agents.clear()
        for prey in self.world.get_preys():
            if self.is_inside(prey):
                self.agents.append(prey)
        
        # If there are no agents inside this HideObject, then color changes to white
        if len(self.agents) == 0:
            self.color = 'WHITE'

    def randomise_loc(self):
        if self.world is not None:
            x = random.randint(0, self.world.cx)
            y = random.randint(0, self.world.cy)
            return Vector2D(x, y)
        else:
            return Vector2D(0, 0)

    def render(self):
        egi.set_pen_color(name=self.color)
        egi.circle(self.pos, self.radius)

        # If there are agents inside this HideObject, then color changes to red
        if len(self.agents) > 0:
            self.color = 'RED'
        else:
            self.color = 'WHITE'
        
    def is_inside(self, agent):
        distance_to_agent = (self.pos - agent.pos).length()
        return distance_to_agent <= self.radius



class World(object):
    def __init__(self, cx, cy):
        self.cx = cx
        self.cy = cy
        self.target = Vector2D(cx / 2, cy / 2)
        self.hide_objects = [HideObject(self, Vector2D(200, 200), 50),
                             HideObject(self, Vector2D(400, 400), 50)]
            
        self.agents = []
        self.paused = True
        self.show_info = True

    def update(self, delta):
        if not self.paused and self.get_preys():
            for agent in self.agents:
                agent.update(delta)
            # Updates all all hiding positions, (checking for agents hiding at it)
            for obj in self.hide_objects:
                obj.update()

        for obj in self.hide_objects:
            obj.update()
            

    def render(self):
        if self.target:
            egi.red_pen()
            egi.cross(self.target, 10)
            
        if self.show_info:
            infotext = ', '.join(set(agent.mode for agent in self.agents))
            egi.white_pen()
            egi.text_at_pos(0, 0, infotext)

            
        for agent in self.agents:
            agent.render()
            
        for obj in self.hide_objects:
            obj.render()

    def wrap_around(self, pos):
        ''' Treat world as a toroidal space. Updates parameter object pos '''
        max_x, max_y = self.cx, self.cy
        if pos.x > max_x:
            pos.x = pos.x - max_x
        elif pos.x < 0:
            pos.x = max_x - pos.x
        if pos.y > max_y:
            pos.y = pos.y - max_y
        elif pos.y < 0:
            pos.y = max_y - pos.y

    def transform_points(self, points, pos, forward, side, scale):
        ''' Transform the given list of points, using the provided position,
            direction and scale, to object world space. '''
        # make a copy of original points (so we don't trash them)
        wld_pts = [pt.copy() for pt in points]
        # create a transformation matrix to perform the operations
        mat = Matrix33()
        # scale,
        mat.scale_update(scale.x, scale.y)
        # rotate
        mat.rotate_by_vectors_update(forward, side)
        # and translate
        mat.translate_update(pos.x, pos.y)
        # now transform all the points (vertices)
        mat.transform_vector2d_list(wld_pts)
        # done
        return wld_pts

    def transform_point(self, point, pos, forward, side):
        ''' Transform the given single point, using the provided position,
        and direction (forward and side unit vectors), to object world space. '''
        # make a copy of the original point (so we don't trash it)
        wld_pt = point.copy()
        # create a transformation matrix to perform the operations
        mat = Matrix33()
        # rotate
        mat.rotate_by_vectors_update(forward, side)
        # and translate
        mat.translate_update(pos.x, pos.y)
        # now transform the point (in place)
        mat.transform_vector2d(wld_pt)
        # done
        return wld_pt

    def get_hunters(self):
        return [agent for agent in self.agents if agent.mode == "hunter"]
    
    def get_preys(self):
        return [agent for agent in self.agents if agent.mode == "prey"]

