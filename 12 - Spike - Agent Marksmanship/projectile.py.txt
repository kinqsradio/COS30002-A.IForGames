from graphics import egi
from vector2d import Vector2D

class Projectile(object):
    """description of class"""
    def __init__(self, world, weapon, target_enemy, damage):
        self.world = world
        self.weapon = weapon
        self.target_enemy = target_enemy
        self.pos = Vector2D()
        self.vel = Vector2D()
        self.max_speed = None
        self.damage = damage
        self.hit = False


    def update(self, delta):
        if not self.hit:
            hit = self.detect_hit()
            if hit:
                hit.received_damage(self.damage)
                self.hit = True

            self.vel.normalise()
            self.vel *= self.max_speed
            # update position
            self.pos += self.vel * delta
        

    def render(self):
        if not self.hit:
            egi.circle(self.pos, 5)


    def detect_hit(self):
        '''check if projectile hit'''
        for enemy in self.world.enemies:
            if enemy.alive:
                to_enemy = enemy.pos - self.pos
                dist = to_enemy.length()
                if dist < enemy.scale.length():
                    # print('Target Hit')
                    return enemy
        return False

    def calculate(self):
        '''prepare to be put back onto the screen'''
        self.max_speed = self.weapon.proj_speed
        self.pos = self.weapon.agent.pos.copy()
        self.vel = (self.target_enemy.pos - self.weapon.agent.pos).normalise() * self.max_speed
