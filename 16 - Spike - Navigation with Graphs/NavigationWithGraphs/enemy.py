from vector2d import Vector2D
from vector2d import Point2D
from graphics import egi, KEY
from math import *
from random import random, randrange, uniform
from path import *
from node import *
from searches import *

class Enemy(object):
    def __init__(self,world = None, pos = None, scale = 30.0, mass = 1.0, mode='wander'):
        self.world = world
        if pos is not None: 
            self.pos = pos
        else: 
            self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.previous_position = Vector2D(self.pos.x, self.pos.y)
        
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
        self.max_force = 200.0
        
        self.separation = 200.0
        
        self.shield = None
        self.shield_strength = None
        
        self.path = Path()
        
        self.mode = mode
        
    def render(self):   
        if self.alive:
            if self.mode == 'follow path':
                if self.path._pts:
                    self.path.render()
                    
                                    
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

            if self.shield_strength is not None:
                shield_ratio = self.shield_strength / 100
                bar_width = self.scale.x * 2
                bar_height = 5
                egi.set_pen_color(name='WHITE')
                egi.rect(self.pos.x - bar_width / 2, self.pos.y + self.scale.y + bar_height + 10, self.pos.x + bar_width / 2, self.pos.y + self.scale.y + bar_height * 2 + 10)
                egi.set_pen_color(name='YELLOW')
                egi.rect(self.pos.x - bar_width / 2, self.pos.y + self.scale.y + bar_height + 10, self.pos.x - bar_width / 2 + bar_width * shield_ratio, self.pos.y + self.scale.y + bar_height * 2 + 10)

    
    def calculate(self, delta): 
        mode = self.mode 
        force = Vector2D(0,0) 
        if mode == 'wander':     
            if self.health < self.max_health * 0.5:
                # Seek nearest health object
                closest_health = None
                closest_distance = float('inf')

                for health in self.world.healths:
                    distance = self.pos.distance(health.pos)
                    if distance < closest_distance:
                        closest_distance = distance
                        closest_health = health

                if closest_health is not None:
                    force = self.seek(closest_health.pos)
            else:
                # Combine wander and separation forces
                wander_force = self.wander(delta)
                separation_force = self.separate()
                force = wander_force + separation_force
        elif mode == 'follow path':
            force = self.follow_path()

        return force

    
    def switch_mode(self):
        ''' Updates state according to different variables '''
        if self.path._pts:
            self.mode = 'follow path'
        else:
            self.mode = 'wander'
            
    def update(self,delta):
        if self.alive:
            
            self.switch_mode()

            if self.mode == 'wander':            
                ''' update vehicle position and orientation '''
                # calculate and set self.force to be applied
                force = self.calculate(delta)
                # force = self.wander(delta)
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
                
                
            elif self.mode == 'follow path':
                 # new velocity
                self.vel = self.calculate(delta)
                # limit velocity
                self.vel.truncate(self.max_speed)
                # update position
                self.pos += self.vel * delta
                
                # update heading is non-zero velocity (moving)
                if self.vel.lengthSq() > 0.00000001:
                    self.heading = self.vel.get_normalised()
                    self.side = self.heading.perp()
                    
             # Check for collision with health object
            for health in self.world.healths:
                if self.is_colliding_with_health(health):
                    self.health += health.heal
                    self.health = min(self.health, self.max_health)
                    health.reset_position()
                    
            # Check for collision with shield object
            if self.shield is None:
                for shield in self.world.shields:
                    if self.is_colliding_with_shield(shield):
                        self.pick_up_shield(shield)
                        shield.reset_position()
            
            if self.world.target is not None and self.pos.distance(self.world.target) < 5:
                # Reset the target and remove the path
                self.world.target = None
                self.path.clear()
                # Switch back to wander mode
                # self.mode = 'wander'
            
        if self.health <= 0:
            self.alive = False

    def received_damage(self, damage):
        if self.shield_strength is not None:  # Check if the shield is equipped
            remaining_shield = self.shield_strength - damage
            if remaining_shield <= 0:  # Shield is broken
                self.health += remaining_shield  # Deduct remaining damage from health
                self.shield_strength = None
                self.shield.enemy = None  # Remove shield from enemy
                self.shield.picked_up = False  # Mark shield as not picked up
                self.shield.reset_position()  # Reset shield position in the world
                self.shield = None  # Remove shield from the enemy
            else:
                self.shield_strength -= damage
        else:
            self.health -= damage

        
    def is_colliding_with_health(self, health):
        distance = self.pos.distance(health.pos)
        collision_distance = self.bRadius + health.scale.x / 2
        return distance < collision_distance
    
    def is_colliding_with_shield(self, shield):
        distance = self.pos.distance(shield.pos)
        collision_distance = self.bRadius + shield.scale.x / 2
        return distance < collision_distance


    def pick_up_shield(self, shield):
        self.shield = shield
        shield.enemy = self
        self.shield_strength = shield.shield_value
        shield.picked_up = True
        print(self.shield_strength)
        
    def has_moved(self):
        return self.pos != self.previous_position

    def follow_path(self):
        if (self.path.is_finished()):
            # Arrives at the final waypoint 
            return self.seek(self.path._pts[-1])
        else:
            if self.current_pos_grid(self.path.current_pt()):
                self.path.inc_current_pt()
            return self.seek(self.path.current_pt())
        
    def update_path(self):
        ''' Reassigns the points of path to head towards new destination'''
        maze = self.world.grid.grid
        start = self.world.grid.get_node(self.pos)
        end = self.world.grid.get_node(self.world.target)
        if self.world.grid.node_available(end):
            pts = astar(maze, start, end)
            for pt in pts:
                pt.x = pt.x * self.world.grid.grid_size + self.world.grid.grid_size/2
                pt.y = pt.y * self.world.grid.grid_size + self.world.grid.grid_size/2
            self.path.set_pts(pts)
    
    def current_pos_grid(self, pos):
        return self.world.grid.get_node(pos) == self.world.grid.get_node(self.pos)
        
    def speed(self):
        return self.vel.length()
    
    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return desired_vel
    
    def seek2(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return desired_vel - self.vel
    

    def arrive(self, target_pos):
        ''' this behaviour is similar to seek() but it attempts to arrive at
            the target position with a zero velocity'''
        decel_rate = 1
        to_target = target_pos - self.pos
        dist = to_target.length()
        # calculate the speed required to reach the target given the
        # desired deceleration rate
        speed = dist / decel_rate
        # make sure the velocity does not exceed the max
        speed = min(speed, self.max_speed)
        # from here proceed just like Seek except we don't need to
        # normalize the to_target vector because we have already gone to the
        to_target.normalise()
        # trouble of calculating its length for dist.
        desired_vel = to_target * speed
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
    
        
    def separate(self):
        # Moves away from nearby enemies
        all_enemies = [e for e in self.world.enemies if e is not self]
        sorted_enemies = sorted(all_enemies, key=lambda e: (e.pos - self.pos).length())

        # Consider only the 5 closest enemies for separation
        closest_enemies = sorted_enemies[:5]

        separation_force = Vector2D()
        for enemy in closest_enemies:
            distance = (self.pos - enemy.pos).length()
            if distance < self.separation:
                to_target = self.pos - enemy.pos
                to_target.normalise()
                to_target *= self.separation - distance
                separation_force += to_target

        return separation_force
    
    