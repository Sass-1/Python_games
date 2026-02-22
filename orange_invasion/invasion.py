from random import randint
import pgzrun
import os

os.environ['SDL_VIDEO_CENTERED'] = '1'

WIDTH = 600
HEIGHT = 600

score = 0
vitesse_orange = 2
game_over = False

orange = Actor("orange")
orange.pos = randint(10,550),0
    
cowboy = Actor("cowboy")
cowboy.pos = 300, 550

bullet = Actor("bullet")
bullet.active = False

sounds.music.play(-1)

def draw ():
    screen.blit("background", (0, 0))
    cowboy.draw()
    orange.draw()
    screen.draw.text("Score: " + str(score), color="white", topleft=(10, 10))
    
    if bullet.active:
        bullet.draw()
    
    if game_over:
        screen.blit("background", (0, 0))
        screen.draw.text("Final Score: " + str(score), center=(WIDTH // 2, HEIGHT // 2), fontsize=60)
    
def update ():
    global score, vitesse_orange, game_over
    orange.y += vitesse_orange
    if orange.y > HEIGHT or orange.colliderect(cowboy):
        if not game_over:
            sounds.music.stop()
            sounds.game_over_sound.play()
            sounds.game_over.play()
            game_over = True
    
    if keyboard.left:
        cowboy.x -= 7
    elif keyboard.right:
        cowboy.x += 7
        
    if cowboy.x < 20 :
        cowboy.x = 20
    elif cowboy.x > 580 :
        cowboy.x = 580
        
    if keyboard.space and not bullet.active and not game_over:
        sounds.shot.play()
        bullet.x = cowboy.x
        bullet.y = cowboy.y -20
        bullet.active = True    
    
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
        vitesse_orange = 2.5
    elif score == 90:
        vitesse_orange = 3.5



pgzrun.go()