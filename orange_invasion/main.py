# -*- coding: utf-8 -*-
import asyncio
import pygame
import os
from random import randint

os.environ['SDL_VIDEO_CENTERED'] = '1'

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 600, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Orange Invasion")

try:
    icon = pygame.image.load("images/my_icon.png")
    pygame.display.set_icon(icon)
except:
    pass

clock = pygame.time.Clock()

class Actor:
    def __init__(self, image_name):
        self.image = pygame.image.load("images/" + image_name + ".png").convert_alpha()
        self.rect = self.image.get_rect()
        self.active = True

    @property
    def x(self):
        return self.rect.centerx
    @x.setter
    def x(self, value):
        self.rect.centerx = int(value)

    @property
    def y(self):
        return self.rect.centery
    @y.setter
    def y(self, value):
        self.rect.centery = int(value)

    @property
    def pos(self):
        return (self.rect.centerx, self.rect.centery)
    @pos.setter
    def pos(self, value):
        self.rect.centerx = int(value[0])
        self.rect.centery = int(value[1])

    def draw(self):
        screen.blit(self.image, self.rect)

    def colliderect(self, other):
        return self.rect.colliderect(other.rect)

background = pygame.image.load("images/background.png").convert()

def load_sound(filename):
    for ext in ["wav", "ogg", "mp3"]:
        path = "sounds/" + filename + "." + ext
        if os.path.exists(path):
            return pygame.mixer.Sound(path)
    return None

def load_music(filename):
    for ext in ["mp3", "ogg", "wav"]:
        path = "sounds/" + filename + "." + ext
        if os.path.exists(path):
            pygame.mixer.music.load(path)
            return True
    return False

shot_sound      = load_sound("shot")
game_over_sound = load_sound("game_over_sound")
game_over_voice = load_sound("game_over")
load_music("music")

font_score = pygame.font.SysFont(None, 36)
font_big   = pygame.font.SysFont(None, 60)
font_small = pygame.font.SysFont(None, 40)

score          = 0
vitesse_orange = 2.0
game_over      = False
compt_heart    = 0

orange  = Actor("orange");      orange.pos  = randint(10, 550), 0
cowboy  = Actor("cowboy");      cowboy.pos  = 300, 550
cowboy1 = Actor("cowboy_mort"); cowboy1.pos = 320, 530

heart3 = Actor("heart3"); heart3.pos = 590, 20; heart3.active = True
heart2 = Actor("heart2"); heart2.pos = 560, 20; heart2.active = True
heart1 = Actor("heart1"); heart1.pos = 530, 20; heart1.active = True

bullet = Actor("bullet"); bullet.active = False

def reset_game():
    global game_over, score, vitesse_orange, compt_heart
    score          = 0
    vitesse_orange = 2.0
    compt_heart    = 0
    game_over      = False
    cowboy.pos     = 300, 550
    orange.pos     = randint(10, 550), 0
    bullet.active  = False
    heart3.active  = True
    heart2.active  = True
    heart1.active  = True

def draw():
    screen.blit(background, (0, 0))

    if heart3.active: heart3.draw()
    if heart2.active: heart2.draw()
    if heart1.active: heart1.draw()

    cowboy.draw()
    orange.draw()

    score_surf = font_score.render("Score: " + str(score), True, (255, 255, 255))
    screen.blit(score_surf, (10, 10))

    if bullet.active:
        bullet.draw()

    if game_over:
        screen.blit(background, (0, 0))
        cowboy1.draw()
        t1 = font_big.render("Final Score: " + str(score), True, (255, 255, 255))
        t2 = font_small.render("Press R to restart", True, (255, 255, 255))
        screen.blit(t1, t1.get_rect(center=(300, 280)))
        screen.blit(t2, t2.get_rect(center=(310, 340)))

    pygame.display.flip()

def update(keys):
    global score, vitesse_orange, game_over, compt_heart

    if game_over:
        if keys[pygame.K_r]:
            reset_game()
            if game_over_sound: game_over_sound.stop()
            if game_over_voice: game_over_voice.stop()
            pygame.mixer.music.play(-1)
        return
    
    orange.y += vitesse_orange

    if orange.y > HEIGHT or orange.colliderect(cowboy):
        compt_heart += 1
        orange.pos = randint(10, 550), 0

        if compt_heart == 1:
            heart3.active = False
        elif compt_heart == 2:
            heart2.active = False
        elif compt_heart >= 3:
            heart1.active = False
            pygame.mixer.music.stop()
            if game_over_sound: game_over_sound.play()
            if game_over_voice: game_over_voice.play()
            game_over = True


    if keys[pygame.K_LEFT]:
        cowboy.x -= 7
    elif keys[pygame.K_RIGHT]:
        cowboy.x += 7

    if cowboy.x < 20:
        cowboy.x = 580
    elif cowboy.x > 580:
        cowboy.x = 20

    if keys[pygame.K_SPACE] and not bullet.active:
        if shot_sound: shot_sound.play()
        bullet.x = cowboy.x
        bullet.y = cowboy.y - 20
        bullet.active = True

    if bullet.active:
        bullet.y -= 10
        if bullet.y < 0:
            bullet.active = False
        elif bullet.colliderect(orange):
            vitesse_orange += 0.1
            score += 10
            bullet.active = False
            orange.pos = randint(10, 550), 0

async def main():
    try:
        pygame.mixer.music.play(-1)
    except:
        pass

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        update(keys)
        draw()
        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
