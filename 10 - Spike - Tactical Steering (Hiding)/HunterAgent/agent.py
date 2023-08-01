'''An agent with Seek, Flee, Arrive, Pursuit behaviours

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

AGENT_MODES = {
    KEY._1: 'seek',
    KEY._2: 'arrive_slow',
    KEY._3: 'arrive_normal',
    KEY._4: 'arrive_fast',
    KEY._5: 'flee',
    KEY._6: 'pursuit',
    KEY._7: 'follow_path',
    KEY._8: 'wander',
}

class Agent(object):

    # NOTE: Class Object (not *instance*) variables!
    DECELERATION_SPEEDS = {
        'slow': 0.1,
        'normal': 1.0,
        'fast': 5.0,
        ### ADD 'normal' and 'fast' speeds here
        # ...
        # ...
    }

    def __init__(self, world=None, mode='prey', scale=30.0, mass=1.0):
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
        ### path to follow?
        self.path = Path()
        self.randomise_path()
        self.waypoint_threshold = 50.0

        ### wander details
        # self.wander_?? ...
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        
        # limits?
        self.max_speed = 20.0 * scale
        self.max_force = 500.0

        # debug draw info?
        self.show_info = False
        
        # agent type        
        if (self.mode == 'hunter'): self.color = 'RED'
        elif (self.mode == 'prey'): self.color = 'BLUE'

        
    def calculate(self, delta):
        # calculate the current steering force based on the agent's mode
        mode = self.mode            
        if mode == 'prey':
            # find the closest hunter agent
            closest_hunter = self.get_closest_agent('hunter')

            # Find the furthest hide object from the hunter
            furthest_hide_obj = self.find_furthest_hide_object_from_agent(closest_hunter)
            if furthest_hide_obj:
                hiding_position, _ = self.get_hiding_position_and_distance(furthest_hide_obj, self.pos)
            else:
                hiding_position = None

            if hiding_position and closest_hunter:
                hiding_force = self.hide_behind_object(closest_hunter.pos)
                fleeing_force = self.flee(closest_hunter.pos)
                force = hiding_force + fleeing_force + self.seek(hiding_position)
            elif hiding_position:
                force = self.seek(hiding_position)
            else:
                force = Vector2D()
        elif mode == 'hunter':
            # find the closest prey agent
            closest_prey = self.get_closest_agent('prey')
            if closest_prey:
                if self.is_prey_hiding(closest_prey):
                    # Calculate a force to avoid the hiding object
                    force = self.avoid_objects()
                else:
                    force = self.seek(closest_prey.pos)
            else:
                force = Vector2D()
        else:
            force = Vector2D()

        self.force = force
        return force

    def find_furthest_hide_object_from_agent(self, agent):
        if not self.world.hide_objects:  # if there are no hide objects
            return None
        distances = [(obj.pos - agent.pos).length() for obj in self.world.hide_objects]
        max_distance_index = distances.index(max(distances))
        return self.world.hide_objects[max_distance_index]

    
    def find_closest_white_hide_object(self):
        white_hide_objs = [obj for obj in self.world.hide_objects if obj.color == 'WHITE']
        if not white_hide_objs:  # if there are no white hide objects
            return None
        distances = [(obj.pos - self.pos).length() for obj in white_hide_objs]
        min_distance_index = distances.index(min(distances))
        return white_hide_objs[min_distance_index]

    def avoid_objects(self):
        avoid_force = Vector2D()
        for obj in self.world.hide_objects:
            # Calculate vector from agent to object
            to_object = self.pos - obj.pos
            # Check if object is near
            if to_object.length() < obj.radius + self.bRadius:
                # Calculate a force to push the agent away from the object
                avoid_force += to_object.normalise() / to_object.length()
        return avoid_force



    def update(self, delta):
        ''' update vehicle position and orientation '''
        # calculate and set self.force to be applied
        force = self.calculate(delta)  # <-- delta needed for wander
        # limit force? <-- for wander
        force.truncate(self.max_force)  # <-- new force limiting code
        # determin the new accelteration
        self.accel = force / self.mass  # not needed if mass = 1.0
        # new velocity
        self.vel += self.accel * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta

        # Ensure the hunter is outside of hiding objects
        if self.mode == 'hunter':
            for hide_object in self.world.hide_objects:
                if (self.pos - hide_object.pos).length() < hide_object.radius + self.bRadius:
                    escape_dir = (self.pos - hide_object.pos).normalise()
                    self.pos = hide_object.pos + escape_dir * (hide_object.radius + self.bRadius)

        # update heading is non-zero velocity (moving)
        if self.vel.length_sq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)


    def render(self, color=None):
        ''' Draw the triangle agent with color'''
        # draw the path if it exists and the mode is follow
        if self.mode == 'follow_path':
            ## ...
            pass

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


        # add some handy debug drawing info lines - force and velocity
        if self.show_info:
            s = 0.5 # <-- scaling factor
            # force
            egi.red_pen()
            egi.line_with_arrow(self.pos, self.pos + self.force * s, 5)
            # velocity
            egi.grey_pen()
            egi.line_with_arrow(self.pos, self.pos + self.vel * s, 5)
            # net (desired) change
            egi.white_pen()
            egi.line_with_arrow(self.pos+self.vel * s, self.pos+ (self.force+self.vel) * s, 5)
            egi.line_with_arrow(self.pos, self.pos+ (self.force+self.vel) * s, 5)

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

    #--------------------------------------------------------------------------

    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)

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

    def arrive(self, target_pos, speed):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = self.DECELERATION_SPEEDS[speed]
        to_target = target_pos - self.pos
        dist = to_target.length()
        if dist > 0:
            # calculate the speed required to reach the target given the
            # desired deceleration rate
            speed = dist / decel_rate
            # make sure the velocity does not exceed the max
            speed = min(speed, self.max_speed)
            # from here proceed just like Seek except we don't need to
            # normalize the to_target vector because we have already gone to the
            # trouble of calculating its length for dist.
            desired_vel = to_target * (speed / dist)
            return (desired_vel - self.vel)
        return Vector2D(0, 0)

    def pursuit(self, evader):
        ''' this behaviour predicts where an agent will be in time T and seeks
            towards that point to intercept it. '''
        ## OPTIONAL EXTRA... pursuit (you'll need something to pursue!)
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

    def follow_path(self):
        if self.path.is_finished():
            return self.arrive(self.path._pts[-1], 'slower')
        else:
            distance_to_way_point = self.pos.distance(self.path.current_pt())
            if distance_to_way_point <= self.waypoint_threshold:
                self.path.inc_current_pt()
            return self.seek(self.path.current_waypoint(), 'fast')
    
    def randomise_path(self):
        cx = self.world.cx  # width
        cy = self.world.cy  # height
        margin = min(cx, cy) * (1/6)  # use this for padding in the next line
        min_dist = 15  # the minimum distance between the waypoints
        minx = margin
        miny = margin
        maxx = cx - margin
        maxy = cy - margin
        self.path.create_random_path(min_dist, minx, miny, maxx, maxy)
        
    def hide_behind_object(self, hunter_pos):
        best_hiding_spot = None
        best_distance = float('-inf')  # changed from 'inf' to '-inf'

        for hide_object in self.world.hide_objects:
            hiding_spot, distance = self.get_hiding_position_and_distance(hide_object, hunter_pos)
            if distance > best_distance:  # changed from '<' to '>'
                best_hiding_spot = hiding_spot
                best_distance = distance

        if best_hiding_spot:
            return self.arrive(best_hiding_spot, 'fast')

        return Vector2D()



    def get_hiding_position_and_distance(self, hide_object, hunter_pos):
        offset = hunter_pos - hide_object.pos  # Use hunter_pos instead of hardcoded position
        hiding_distance = hide_object.radius + self.bRadius
        hiding_position = hide_object.pos - offset.normalise() * hiding_distance

        distance = hiding_position.distance(self.pos)
        return hiding_position, distance
