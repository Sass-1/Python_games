from random import randint
import pgzrun
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 400
HEIGHT = 400

score = 0

orange = Actor("orange")
orange.pos = randint(10,350),0
    
cowboy = Actor("cowboy")
cowboy.pos = 200, 350

bullet = Actor("bullet")
bullet.active = False


def draw ():
    screen.fill((100, 200, 100))
    cowboy.draw()
    orange.draw()
    screen.draw.text("Score: " + str(score), color="black", topleft=(10, 10))
    if bullet.active:
        bullet.draw()
    
def update ():
    global score
    orange.y += 0.5
    if orange.y > HEIGHT or orange.colliderect(cowboy):
        quit ()
    
    if keyboard.left:
        cowboy.x -= 2
    elif keyboard.right:
        cowboy.x += 2 
    if cowboy.x < 20 :
        cowboy.x = 20
    elif cowboy.x > 380 :
        cowboy.x = 380
    
    if bullet.active:
        bullet.y -= 4
        
    if bullet.y < 0:
        bullet.active = False
    elif bullet.colliderect(orange):
        score += 10
        bullet.active = False
        orange.pos = randint(10,350),0


def on_mouse_down (pos):
    if not bullet.active:  
        bullet.x = cowboy.x
        bullet.y = cowboy.y -20
        bullet.active = True


pgzrun.go()