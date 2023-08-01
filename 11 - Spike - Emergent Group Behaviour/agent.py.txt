'''An agent with Seek, Flee, Arrive, Pursuit behaviours

Created for COS30002 AI for Games, by Clinton Woodward <cwoodward@swin.edu.au>
For class use only. Do not publically share or post this code without permission.

'''

from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import sin, cos, radians
from random import random, randrange, uniform

AGENT_MODES = {
    KEY._1: 'wander',
    KEY._2: 'cohesion',
    KEY._3: 'separation',
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.1,
        'normal': 1.0,
        'fast': 2.0,
    }

    def __init__(self, world=None, scale=30.0, mass=1.0, mode='seek'):
        # keep a reference to the world object
        self.world = world
        self.mode = mode
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

        # data for drawing this agent
        self.color = 'ORANGE'
        self.vehicle_shape = [
            Point2D(-1.0,  0.6),
            Point2D( 1.0,  0.0),
            Point2D(-1.0, -0.6)
        ]

        ### wander details
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 3.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 0.5 * scale
        self.bRadius = scale
        
        # limits?
        self.max_speed = 20.0 * scale
        self.max_force = 500.0
        
        self.cohesion_weight = 400.0
        self.separation_weight = 100.0
        self.alignment_weight = 200.0
        self.wander_weight = 100

        self.cohesion_radius = 100
        self.separation_radius = 50
        self.alignment_radius = 100

        # debug draw info?
        self.show_info = False
            

    def calculate(self, delta, close_neighbors):
        if self.mode == 'separation':
            combined_force = self.separation(close_neighbors) * self.separation_weight
        else:
            wander_force = self.wander(delta)
            cohesion_force = self.cohesion(close_neighbors)
            alignment_force = self.alignment(close_neighbors)

            combined_force = (wander_force * self.wander_weight +
                            cohesion_force * self.cohesion_weight +
                            alignment_force * self.alignment_weight)

        return combined_force
    

    def update(self, delta):
        ''' update vehicle position and orientation '''
        close_neighbors = self.get_neighbors(self.wander_radius)
        
        # calculate and set self.force
        self.force = self.calculate(delta, close_neighbors)
        # new acceleration due to force
        self.accel = self.force / self.mass
        # new velocity
        self.vel += self.accel * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading if non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
                

    def render(self, color=None):
        # draw the ship
        egi.set_pen_color(name=self.color)
        pts = self.world.transform_points(self.vehicle_shape, self.pos,
                                          self.heading, self.side, self.scale)
        # draw it!
        egi.closed_shape(pts)
        
        # draw wander info?
        if self.mode == 'wander':
            # calculate the center of the wander circle in front of the agent
            wnd_pos = Vector2D(self.wander_dist, 0)
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            # draw the wander circle
            egi.green_pen()
            egi.circle(wld_pos, self.wander_radius)
            # draw the wander target (little circle on the big circle)
            egi.red_pen()
            wnd_pos = (self.wander_target + Vector2D(self.wander_dist, 0))
            wld_pos = self.world.transform_point(wnd_pos, self.pos, self.heading, self.side)
            egi.circle(wld_pos, 3)


    def get_neighbors(self, radius):
        neighbors = []
        for agent in self.world.agents:
            if agent != self:
                distance = (agent.pos - self.pos).length()
                if distance <= radius:
                    neighbors.append(agent)

        return neighbors


    def speed(self):
        return self.vel.length()
    
    def get_closest_agent(self, mode):
        agents = [agent for agent in self.world.agents if agent.mode == mode]
        if not agents:
            return None
        return min(agents, key=lambda obj: (obj.pos - self.pos).length())
    
    def is_prey_hiding(self, prey):
        for hide_object in self.world.hide_objects:
            hiding_position, _ = prey.get_hiding_position_and_distance(hide_object, self.pos)
            if (prey.pos - hiding_position).length() < self.bRadius:
                return True
        return False
    
    def closest(self, neighbors):
        min_distance = float('inf')
        closest_agent = None

        for agent in neighbors:
            distance = (agent.pos - self.pos).length()
            if distance < min_distance:
                min_distance = distance
                closest_agent = agent

        return closest_agent

    #--------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)
    
    def cohesion(self, close_neighbors):
        center_of_mass = Vector2D()
        count = 0

        for agent in close_neighbors:
            center_of_mass += agent.pos
            count += 1

        if count > 0:
            center_of_mass /= count
            return center_of_mass
        else:
            return Vector2D()
    
    def separation(self, close_neighbors):
        if not close_neighbors:
            return Vector2D()

        # Assuming you have a function to find the closest agent
        closest_agent = self.closest(close_neighbors)
        closest_agent_pos = closest_agent.pos
        target = (2 * self.pos - closest_agent_pos)
        to_target = target - self.pos

        return to_target

    def alignment(self, close_neighbors):
        average_heading = Vector2D()
        count = 0

        for agent in close_neighbors:
            average_heading += agent.heading
            count += 1

        if count > 0:
            average_heading /= count
            average_heading -= self.heading
            return average_heading
        else:
            return Vector2D()

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

    def flee(self, hunter_pos):
        ''' move away from hunter position '''
        panic_distance = 100
        distance_vector = self.pos - hunter_pos
        distance = hunter_pos.distance(self.pos)
        if distance <= panic_distance:
            flee_direction = distance_vector.normalise() * self.max_speed
            return flee_direction
        else:
            return Vector2D()
    