from graphics import egi, KEY
from pyglet import window, clock
from pyglet.gl import *

from vector2d import Vector2D
from world import World
from agent import Agent
from enemy import Enemy
from weapon import *
from health import *
from shield import *

SCREEN_WIDTH = 1270
SCREEN_HEIGHT = 720

def on_key_press(symbol, modifiers):
    if symbol == KEY.P:
        world.paused = not world.paused
    elif symbol == KEY.W:
        world.healths.append(Health(world))
    elif symbol == KEY.S:
        world.shields.append(Shield(world))
    elif symbol == KEY.A:
        world.agents.append(Agent(world))
    elif symbol == KEY.I:
        for agent in world.agents:
            agent.show_info = not agent.show_info
    elif symbol == KEY.T:
        world.enemies.append(Enemy(world))
    elif symbol == KEY._1:
        for agent in world.agents:
            agent.switch_weapon('Rifle')
    elif symbol == KEY._2:
        for agent in world.agents:
            agent.switch_weapon('Rocket')
    elif symbol == KEY._3:
        for agent in world.agents:
            agent.switch_weapon('Hand Gun')
    elif symbol == KEY._4:
        for agent in world.agents:
            agent.switch_weapon('Handgrenade')

def on_mouse_press(x, y, button, modifiers):
    pass

def on_resize(cx, cy):
    world.cx = cx
    world.cy = cy

if __name__ == '__main__':
    # create a pyglet window and set glOptions
    win = window.Window(width=SCREEN_WIDTH, height=SCREEN_HEIGHT, vsync=True, resizable=True)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    # needed so that egi knows where to draw
    egi.InitWithPyglet(win)
    # prep the fps display
    fps_display = window.FPSDisplay(win)
    # register key and mouse event handlers
    win.push_handlers(on_key_press)
    win.push_handlers(on_resize)
    win.push_handlers(on_mouse_press)

    # create a world for agents
    world = World(SCREEN_WIDTH, SCREEN_HEIGHT)
    # add one agent
    world.agents.append(Agent(world))

    num_pickable = 5
    for _ in range(num_pickable):
        world.healths.append(Health(world))
        world.shields.append(Shield(world))
    
    # unpause the world ready for movement
    world.paused = False

    while not win.has_exit:
        win.dispatch_events()
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        # show nice FPS bottom right (default)
        delta = clock.tick()
        world.update(delta)
        world.render()
        fps_display.draw()
        # swap the double buffer
        win.flip()

