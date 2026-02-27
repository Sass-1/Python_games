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

cowboy1 = Actor("cowboy_mort")
cowboy1.pos = 320, 530 

heart3 = Actor("heart3")
heart3.pos = 590, 20

heart2 = Actor("heart2")
heart2.pos = 560, 20

heart1 = Actor("heart1")
heart1.pos = 530, 20

bullet = Actor("bullet")
bullet.active = False

sounds.music.play(-1)

def reset_game ():
    global game_over,score,vitesse_orange
    score = 0
    game_over = False
    cowboy.pos = 300, 550
    orange.pos = randint(10,550),0
    vitesse_orange = 2

def draw ():
    screen.blit("background", (0, 0))
    heart3.draw()
    heart2.draw()
    heart1.draw()
    cowboy.draw()
    orange.draw()
    screen.draw.text("Score: " + str(score), color="white", topleft=(10, 10))
    
    if bullet.active:
        bullet.draw()
    
    if game_over :
        screen.blit("background", (0, 0))
        screen.draw.text("Final Score: " + str(score), center=(300, 280), fontsize=60)
        screen.draw.text("Press R to restart ", color="white", center=(310, 330) )
        cowboy1.draw()
    
def update ():
    global score, vitesse_orange, game_over
    orange.y += vitesse_orange
    if orange.y > HEIGHT or orange.colliderect(cowboy):
        if not game_over:
            sounds.music.stop()
            sounds.game_over_sound.play()
            sounds.game_over.play()
            game_over = True
            
    if game_over:
        if keyboard.r:
            reset_game()
            sounds.game_over_sound.stop()
            sounds.game_over.stop()
            sounds.music.play(-1) 
        return        
    
    if keyboard.left:
        cowboy.x -= 7
    elif keyboard.right:
        cowboy.x += 7
        
    if cowboy.x < 20 :
        cowboy.x = 580
    elif cowboy.x > 580 :
        cowboy.x = 20
        
    if keyboard.space and not bullet.active and not game_over:
        sounds.shot.play()
        bullet.x = cowboy.x
        bullet.y = cowboy.y -20
        bullet.active = True    
    
    if bullet.active:
        bullet.y -= 10
        
    if bullet.y < 0:
        bullet.active = False
    elif bullet.colliderect(orange):
        vitesse_orange += 0.1
        score += 10
        bullet.active = False
        orange.pos = randint(10,550),0
   
    '''if score == 50:
        vitesse_orange = 2.5
    elif score == 90:
        vitesse_orange = 3
    elif score == 130:
        vitesse_orange = 3.5
    elif score == 170:
        vitesse_orange = 4
    elif score == 210 :
        vitesse_orange = 4.5'''



pgzrun.go()