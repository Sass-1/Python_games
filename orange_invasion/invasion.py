import pgzrun
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 400
HEIGHT = 400

cowboy = Actor("cowboy")
cowboy.pos = 200, 350

bullet = Actor("bullet")
bullet.active = False

def draw ():
    screen.fill((100, 200, 100))
    cowboy.draw()

pgzrun.go()