from projectile import Projectile
from point2d import Point2D
from graphics import egi, KEY
from random import randrange

class Weapon(object):
    def __init__(self, agent=None, world=None, damage=10, proj_speed=2000.0, accuracy=2.0, fire_rate=20, color='WHITE'):
        self.proj_speed = proj_speed
        self.accuracy = accuracy
        self.fire_rate = fire_rate
        self.color = color
        self.fire_rate_tmr = self.fire_rate
        self.damage = damage
        
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
        proj = Projectile(self.world, self, target_enemy, self.damage)
        proj.calculate()
        self.projectiles.append(proj)


