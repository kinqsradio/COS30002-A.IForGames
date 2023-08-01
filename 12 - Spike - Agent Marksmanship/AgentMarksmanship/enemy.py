from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import *
from random import random, randrange, uniform

class Enemy(object):
    def __init__(self,world = None, pos = None, scale = 30.0, mass = 1.0):
        self.world = world
        if pos is not None: 
            self.pos = pos
        else: 
            self.pos = Vector2D(randrange(world.cx), randrange(world.cy))

        self.alive = True
        self.max_health = randrange(50,200)
        self.health = self.max_health
        self.color = 'RED'
        
        # where am i and where am i going? random start pos
        dir = radians(random()*360)
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  # easy scaling of agent size
        self.force = Vector2D()  # current steering force
        self.accel = Vector2D() # current acceleration due to force
        self.mass = mass
        
        
        self.vehicle_shape = [
            Point2D(-1.0,  0.6),
            Point2D( 1.0,  0.0),
            Point2D(-1.0, -0.6)
        ]
        
         ### wander details
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        
        # limits?
        self.max_speed = 20.0 * scale
        self.max_force = 500.0
        
    def render(self):
        if self.alive:
            egi.set_pen_color(name=self.color)
            pts = self.world.transform_points(self.vehicle_shape, self.pos,
                                            self.heading, self.side, self.scale)
            # draw it!
            egi.closed_shape(pts)

            # Draw health bar
            health_ratio = self.health / self.max_health
            bar_width = self.scale.x * 2
            bar_height = 5
            egi.set_pen_color(name='WHITE')
            egi.rect(self.pos.x - bar_width / 2, self.pos.y + self.scale.y + 5, self.pos.x + bar_width / 2, self.pos.y + self.scale.y + 5 + bar_height)
            egi.set_pen_color(name='RED')
            egi.rect(self.pos.x - bar_width / 2, self.pos.y + self.scale.y + 5, self.pos.x - bar_width / 2 + bar_width * health_ratio, self.pos.y + self.scale.y + 5 + bar_height)


    def update(self,delta):
        if self.alive:
            # calculate and set self.force to be applied
            ## force = self.calculate()
            force = self.wander(delta)
            ## limit force? <-- for wander
            force.truncate(self.max_force)
            # determine the new acceleration
            self.accel = force / self.mass  # not needed if mass = 1.0
            # new velocity
            self.vel += self.accel * delta
            # check for limits of new velocity
            self.vel.truncate(self.max_speed)
            # update position
            self.pos += self.vel * delta
            # update heading is non-zero velocity (moving)
            if self.vel.lengthSq() > 0.00000001:
                self.heading = self.vel.get_normalised()
                self.side = self.heading.perp()
            # treat world as continuous space - wrap new position if needed
            self.world.wrap_around(self.pos)
            
            
        if self.health <= 0:
            self.alive = False

    def received_damage(self, damage):
        self.health -= damage
        
    def speed(self):
        return self.vel.length()
    
    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)
    
    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
        wt = self.wander_target
        # this behaviour is dependent on the update rate, so this line must
        # be included when using time independent framerate.
        jitter_tts = self.wander_jitter * delta # this time slice
        # first, add a small random vector to the target's position
        wt += Vector2D(uniform(-1,1) * jitter_tts, uniform(-1,1) * jitter_tts)
        # re-project this new vector back on to a unit circle
        wt.normalise()
        # increase the length of the vector to the same as the radius
        # of the wander circle
        wt *= self.wander_radius
        # move the target into a position WanderDist in front of the agent
        target = wt + Vector2D(self.wander_dist, 0)
        # project the target into world space
        wld_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        # and steer towards it
        return self.seek(wld_target)
