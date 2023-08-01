from projectile import Projectile
from point2d import Point2D
from graphics import egi, KEY
from random import randrange

class Weapon(object):
    def __init__(self, agent=None, world=None, damage=10, proj_speed=2000.0, accuracy=2.0, fire_rate=20, color='WHITE', max_ammo=10, reload_time=3.0):
        self.proj_speed = proj_speed
        self.accuracy = accuracy
        self.fire_rate = fire_rate
        self.color = color
        self.fire_rate_tmr = self.fire_rate
        self.damage = damage
        self.max_ammo = max_ammo
        self.current_ammo = max_ammo
        self.reload_time = reload_time
        self.reload_timer = 0.0
        self.reloading = False
        
        self.projectiles = []
        self.agent = agent
        self.world = world
        self.color = color
        


    def update(self,delta):
        # Update position of all projectiles
        for proj in self.projectiles:
            proj.update(delta)
            if proj.hit:
                self.projectiles.remove(proj)
                
        # Update reload timer
        if self.reloading:
            self.reload_timer -= delta
            if self.reload_timer <= 0:
                self.current_ammo = self.max_ammo
                self.reloading = False



    def render(self):
        egi.set_pen_color(name=self.color)

        # Set the weapon position, radius, and orientation
        weapon_pos = self.agent.pos
        weapon_radius = 5

        # Draw a circle for the weapon
        egi.circle(weapon_pos, weapon_radius)
        
        for proj in self.projectiles:
            proj.render()

    def shoot(self, target_enemy):
        if self.current_ammo > 0 and not self.reloading:
            proj = Projectile(self.world, self, target_enemy, self.damage)
            proj.calculate()
            self.projectiles.append(proj)
            self.current_ammo -= 1
        elif self.current_ammo == 0 and not self.reloading:
            self.reloading = True
            self.reload_timer = self.reload_time
