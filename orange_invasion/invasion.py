from random import randint
import pgzrun
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 600
HEIGHT = 600

 

score = 0
vitesse_orange = 2

orange = Actor("orange")
orange.pos = randint(10,550),0
    
cowboy = Actor("cowboy")
cowboy.pos = 300, 550

bullet = Actor("bullet")
bullet.active = False
sounds.music.play(-1)

def draw ():
    screen.fill((100, 200, 100))
    cowboy.draw()
    orange.draw()
    screen.draw.text("Score: " + str(score), color="black", topleft=(10, 10))
    if bullet.active:
        bullet.draw()
    
def update ():
    global score, vitesse_orange
    orange.y += vitesse_orange
    if orange.y > HEIGHT or orange.colliderect(cowboy):
        quit ()
    
    if keyboard.left:
        cowboy.x -= 4
    elif keyboard.right:
        cowboy.x += 4
    if cowboy.x < 20 :
        cowboy.x = 20
    elif cowboy.x > 580 :
        cowboy.x = 580
    
    if bullet.active:
        bullet.y -= 4
        
    if bullet.y < 0:
        bullet.active = False
    elif bullet.colliderect(orange):
        '''sounds.explosion.play()'''
        score += 10
        bullet.active = False
        orange.pos = randint(10,550),0
   
    if score == 50:
        vitesse_orange = 3.5
    elif score == 90:
        vitesse_orange = 4.5

def on_mouse_down (pos):
    if not bullet.active:
        sounds.shot.play()
        bullet.x = cowboy.x
        bullet.y = cowboy.y -20
        bullet.active = True


pgzrun.go()