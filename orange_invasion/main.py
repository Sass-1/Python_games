# -*- coding: utf-8 -*-
import asyncio
import pygame
import os
import math
from random import randint, random, choice

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

is_mobile = False
try:
    import js
    is_mobile = js.window.innerWidth < 768
except:
    pass

# =============================================================================
# ACTOR CLASS — float positions to avoid stuttering
# =============================================================================
class Actor:
    def __init__(self, image_name, scale=1.0):
        img = pygame.image.load("images/" + image_name + ".png").convert_alpha()
        if scale != 1.0:
            w = int(img.get_width() * scale)
            h = int(img.get_height() * scale)
            img = pygame.transform.scale(img, (w, h))
        self.image = img
        self.rect  = self.image.get_rect()
        self.active = True
        self._fx = float(self.rect.centerx)
        self._fy = float(self.rect.centery)

    @property
    def x(self): return self._fx
    @x.setter
    def x(self, v):
        self._fx = float(v)
        self.rect.centerx = int(v)

    @property
    def y(self): return self._fy
    @y.setter
    def y(self, v):
        self._fy = float(v)
        self.rect.centery = int(v)

    @property
    def pos(self): return (self._fx, self._fy)
    @pos.setter
    def pos(self, v):
        self._fx = float(v[0]); self.rect.centerx = int(v[0])
        self._fy = float(v[1]); self.rect.centery = int(v[1])

    def draw(self): screen.blit(self.image, self.rect)
    def colliderect(self, other): return self.rect.colliderect(other.rect)

# =============================================================================
# LOAD ASSETS
# =============================================================================
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
life_lost_sound = load_sound("life_lost")
powerup_sound   = load_sound("powerup")
load_music("music")

# =============================================================================
# FONTS
# =============================================================================
font_score     = pygame.font.SysFont(None, 36)
font_big       = pygame.font.SysFont(None, 65)
font_small     = pygame.font.SysFont(None, 40)
font_btn       = pygame.font.SysFont(None, 50)
font_combo     = pygame.font.SysFont(None, 46)
font_title     = pygame.font.SysFont(None, 68)
font_medium    = pygame.font.SysFont(None, 44)
font_countdown = pygame.font.SysFont(None, 180)

# =============================================================================
# GAME STATES
# =============================================================================
STATE_DIFFICULTY = "difficulty"
STATE_COUNTDOWN  = "countdown"
STATE_PLAYING    = "playing"
STATE_PAUSED     = "paused"
STATE_GAMEOVER   = "gameover"

game_state = STATE_DIFFICULTY
difficulty = "NORMAL"

# =============================================================================
# GAME VARIABLES
# =============================================================================
score             = 0
high_score        = 0
vitesse_orange    = 2.0
compt_heart       = 0
countdown_val     = 3
countdown_timer   = 0
COUNTDOWN_DELAY   = 70
flash_timer       = 0
FLASH_DURATION    = 18
double_shot_timer = 0
powerup           = None
powerup_spawn_counter = 0
POWERUP_INTERVAL  = 450

# =============================================================================
# ACTORS
# =============================================================================
cowboy  = Actor("cowboy");      cowboy.pos  = 300, 550
cowboy1 = Actor("cowboy_mort"); cowboy1.pos = 320, 530
heart3  = Actor("heart3"); heart3.pos = 590, 20; heart3.active = True
heart2  = Actor("heart2"); heart2.pos = 560, 20; heart2.active = True
heart1  = Actor("heart1"); heart1.pos = 530, 20; heart1.active = True
bullet  = Actor("bullet"); bullet.active  = False
bullet2 = Actor("bullet"); bullet2.active = False

# =============================================================================
# ORANGE TYPES
# =============================================================================
ORANGE_TYPES = [
    {"type": "normal", "scale": 1.0,  "speed_mult": 1.0,  "points": 10, "weight": 60},
    {"type": "small",  "scale": 0.6,  "speed_mult": 1.7,  "points": 20, "weight": 25},
    {"type": "big",    "scale": 1.55, "speed_mult": 0.55, "points": 5,  "weight": 15},
]
oranges = []

def spawn_orange():
    weights = [t["weight"] for t in ORANGE_TYPES]
    total   = sum(weights)
    r       = random() * total
    cumul   = 0
    chosen  = ORANGE_TYPES[0]
    for t in ORANGE_TYPES:
        cumul += t["weight"]
        if r <= cumul:
            chosen = t
            break
    actor = Actor("orange", scale=chosen["scale"])
    actor.pos = randint(20, 580), -20
    return {"actor": actor, "speed_mult": chosen["speed_mult"],
            "points": chosen["points"], "type": chosen["type"]}

oranges.append(spawn_orange())

# =============================================================================
# POWER-UP
# =============================================================================
def make_powerup_surf(ptype):
    surf = pygame.Surface((44, 44), pygame.SRCALPHA)
    if ptype == "life":
        color = (255, 80, 120)
        pygame.draw.circle(surf, color, (13, 14), 11)
        pygame.draw.circle(surf, color, (31, 14), 11)
        pygame.draw.polygon(surf, color, [(2,16),(22,40),(42,16),(31,8),(22,14),(13,8)])
    else:
        color = (255, 220, 0)
        pts = []
        for i in range(10):
            angle = math.pi / 5 * i - math.pi / 2
            rr = 20 if i % 2 == 0 else 9
            pts.append((22 + rr * math.cos(angle), 22 + rr * math.sin(angle)))
        pygame.draw.polygon(surf, color, pts)
        pygame.draw.polygon(surf, (255, 160, 0), pts, 2)
    return surf

def spawn_powerup_obj():
    ptype = choice(["life", "double_shot"])
    return {"surf": make_powerup_surf(ptype),
            "rect": pygame.Rect(randint(20, 556), -20, 44, 44),
            "type": ptype}

# =============================================================================
# PARTICLES
# =============================================================================
particles = []

def spawn_particles(x, y, color=(255, 140, 0)):
    for _ in range(14):
        angle = random() * math.pi * 2
        speed = random() * 4.5 + 1
        particles.append({
            "x": float(x), "y": float(y),
            "vx": math.cos(angle) * speed,
            "vy": math.sin(angle) * speed - 1,
            "life": 35, "max_life": 35,
            "color": color, "size": randint(3, 7)
        })

def update_particles():
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.18
        p["life"] -= 1
        if p["life"] <= 0:
            particles.remove(p)

def draw_particles():
    for p in particles:
        alpha = int(255 * p["life"] / p["max_life"])
        size  = max(1, int(p["size"] * p["life"] / p["max_life"]))
        s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p["color"], alpha), (size, size), size)
        screen.blit(s, (int(p["x"]) - size, int(p["y"]) - size))

# =============================================================================
# FLOATING TEXTS
# =============================================================================
float_texts = []

def add_float_text(text, x, y, color=(255, 255, 100)):
    float_texts.append({"text": text, "x": float(x), "y": float(y),
                         "life": 55, "color": color})

def update_float_texts():
    for t in float_texts[:]:
        t["y"] -= 1.4
        t["life"] -= 1
        if t["life"] <= 0:
            float_texts.remove(t)

def draw_float_texts():
    for t in float_texts:
        alpha = int(255 * t["life"] / 55)
        surf  = font_combo.render(t["text"], True, t["color"])
        surf.set_alpha(alpha)
        screen.blit(surf, surf.get_rect(center=(int(t["x"]), int(t["y"]))))

# =============================================================================
# BACKGROUND TINT
# =============================================================================
def draw_bg_tint():
    intensity = min(score // 40, 10)
    if intensity > 0:
        tint = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        tint.fill((15, 0, 35, intensity * 9))
        screen.blit(tint, (0, 0))

# =============================================================================
# TOUCH BUTTONS
# =============================================================================
# =============================================================================
# TOUCH / SWIPE CONTROLS (mobile)
# =============================================================================
touch_left  = False
touch_right = False
touch_shoot = False

# Swipe tracking
swipe_start_x   = None
swipe_start_y   = None
touch_finger_x  = None  # current finger X for live movement
SWIPE_THRESHOLD = 8     # pixels before considered a swipe

# Pause button (mobile only — small top-right corner)
btn_pause_mob = pygame.Rect(WIDTH - 60, 10, 50, 40)

def draw_pause_btn_mobile():
    draw_btn_generic(btn_pause_mob, "II")
btn_restart   = pygame.Rect(WIDTH//2 - 80, 430, 160, 55)

def draw_btn_generic(rect, label, pressed=False, color_pressed=(255,255,255,130),
                     color_normal=(255,255,255,60)):
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    color = color_pressed if pressed else color_normal
    pygame.draw.rect(surf, color, surf.get_rect(), border_radius=12)
    pygame.draw.rect(surf, (255,255,255,180), surf.get_rect(), width=2, border_radius=12)
    screen.blit(surf, rect.topleft)
    text = font_btn.render(label, True, (255,255,255))
    screen.blit(text, text.get_rect(center=rect.center))

def draw_touch_buttons():
    # Just show the pause button + a small swipe hint at the bottom
    draw_pause_btn_mobile()
    hint = font_score.render("Swipe to move  |  Tap cowboy to shoot", True, (200, 200, 200))
    hint.set_alpha(140)
    screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT - 18)))

def draw_restart_btn():
    surf = pygame.Surface((160, 55), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255,255,255,80),  surf.get_rect(), border_radius=10)
    pygame.draw.rect(surf, (255,255,255,200), surf.get_rect(), width=2, border_radius=10)
    screen.blit(surf, btn_restart.topleft)
    text = font_small.render("RESTART", True, (255,255,255))
    screen.blit(text, text.get_rect(center=btn_restart.center))

# =============================================================================
# DIFFICULTY SCREEN
# =============================================================================
btn_easy   = pygame.Rect(WIDTH//2 - 110, 280, 220, 58)
btn_normal = pygame.Rect(WIDTH//2 - 110, 360, 220, 58)
btn_hard   = pygame.Rect(WIDTH//2 - 110, 440, 220, 58)

def draw_difficulty_screen():
    screen.blit(background, (0, 0))
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    screen.blit(ov, (0, 0))
    title = font_title.render("ORANGE INVASION", True, (255, 140, 0))
    screen.blit(title, title.get_rect(center=(WIDTH//2, 150)))
    sub = font_small.render("SELECT DIFFICULTY", True, (220, 220, 220))
    screen.blit(sub, sub.get_rect(center=(WIDTH//2, 220)))
    if not is_mobile:
        hint = font_score.render("Keyboard: 1 / 2 / 3", True, (150, 150, 150))
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, 530)))
    if high_score > 0:
        hs = font_score.render("Best Score: " + str(high_score), True, (255, 220, 100))
        screen.blit(hs, hs.get_rect(center=(WIDTH//2, 560 if not is_mobile else 530)))

    def draw_diff_btn(rect, label, color):
        s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        pygame.draw.rect(s, (*color, 190), s.get_rect(), border_radius=10)
        pygame.draw.rect(s, (255,255,255,200), s.get_rect(), width=2, border_radius=10)
        screen.blit(s, rect.topleft)
        t = font_medium.render(label, True, (255,255,255))
        screen.blit(t, t.get_rect(center=rect.center))

    draw_diff_btn(btn_easy,   "EASY   [1]" if not is_mobile else "EASY",   (34, 139, 34))
    draw_diff_btn(btn_normal, "NORMAL [2]" if not is_mobile else "NORMAL", (200, 120,  0))
    draw_diff_btn(btn_hard,   "HARD   [3]" if not is_mobile else "HARD",   (180,  20, 20))
    pygame.display.flip()

# =============================================================================
# COUNTDOWN
# =============================================================================
def draw_countdown_screen():
    screen.blit(background, (0, 0))
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 110))
    screen.blit(ov, (0, 0))
    label = str(countdown_val) if countdown_val > 0 else "GO!"
    color = (255, 80, 80) if countdown_val > 0 else (80, 255, 80)
    t = font_countdown.render(label, True, color)
    screen.blit(t, t.get_rect(center=(WIDTH//2, HEIGHT//2)))
    diff_t = font_score.render("Difficulty: " + difficulty, True, (200, 200, 200))
    screen.blit(diff_t, diff_t.get_rect(center=(WIDTH//2, HEIGHT//2 + 110)))
    pygame.display.flip()

# =============================================================================
# PAUSE OVERLAY
# =============================================================================
def draw_pause_overlay():
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 150))
    screen.blit(ov, (0, 0))
    t1 = font_big.render("PAUSED", True, (255, 255, 255))
    screen.blit(t1, t1.get_rect(center=(WIDTH//2, HEIGHT//2 - 30)))
    if is_mobile:
        resume_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 20, 160, 55)
        draw_btn_generic(resume_rect, "RESUME")
    else:
        t2 = font_small.render("Press P to resume", True, (200, 200, 200))
        screen.blit(t2, t2.get_rect(center=(WIDTH//2, HEIGHT//2 + 30)))
    pygame.display.flip()

# =============================================================================
# RESET
# =============================================================================
def reset_game():
    global score, vitesse_orange, compt_heart, game_state
    global countdown_val, countdown_timer, double_shot_timer
    global powerup, powerup_spawn_counter, flash_timer

    score                 = 0
    vitesse_orange        = {"EASY": 1.4, "NORMAL": 2.0, "HARD": 3.0}[difficulty]
    compt_heart           = 0
    countdown_val         = 3
    countdown_timer       = 0
    double_shot_timer     = 0
    flash_timer           = 0
    powerup               = None
    powerup_spawn_counter = 0
    cowboy.pos   = 300, 550
    bullet.active  = False
    bullet2.active = False
    heart3.active  = True
    heart2.active  = True
    heart1.active  = True
    oranges.clear()
    oranges.append(spawn_orange())
    particles.clear()
    float_texts.clear()
    game_state = STATE_COUNTDOWN

# =============================================================================
# DRAW
# =============================================================================
def draw():
    global flash_timer

    screen.blit(background, (0, 0))
    draw_bg_tint()

    if heart3.active: heart3.draw()
    if heart2.active: heart2.draw()
    if heart1.active: heart1.draw()

    cowboy.draw()

    for o in oranges:
        o["actor"].draw()
        # Only show x2 label for small oranges
        if o["type"] == "small":
            lbl = font_score.render("x2", True, (255, 220, 80))
            screen.blit(lbl, (o["actor"].x - 8, o["actor"].y - 28))

    score_surf = font_score.render("Score: " + str(score), True, (255, 255, 255))
    hs_surf    = font_score.render("Best: "  + str(high_score), True, (255, 220, 100))
    screen.blit(score_surf, (10, 10))
    screen.blit(hs_surf,    (10, 40))

    if not is_mobile:
        p_hint = font_score.render("[P] Pause", True, (150, 150, 150))
        screen.blit(p_hint, (10, HEIGHT - 30))

    if double_shot_timer > 0:
        sec = double_shot_timer // 60 + 1
        ds  = font_score.render("DOUBLE SHOT " + str(sec) + "s", True, (255, 220, 0))
        screen.blit(ds, ds.get_rect(center=(WIDTH//2, 20)))

    if bullet.active:  bullet.draw()
    if bullet2.active: bullet2.draw()

    if powerup:
        screen.blit(powerup["surf"], powerup["rect"])
        pulse = int(abs(math.sin(pygame.time.get_ticks() * 0.005)) * 3)
        pygame.draw.circle(screen, (255,220,0), powerup["rect"].center, 26+pulse, 2)

    draw_particles()
    draw_float_texts()

    if flash_timer > 0:
        alpha = int(180 * flash_timer / FLASH_DURATION)
        fs = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        fs.fill((255, 0, 0, alpha))
        screen.blit(fs, (0, 0))
        flash_timer -= 1

    if is_mobile and game_state == STATE_PLAYING:
        draw_touch_buttons()

    if game_state == STATE_GAMEOVER:
        ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        screen.blit(ov, (0, 0))
        cowboy1.draw()
        t1 = font_big.render("GAME OVER", True, (255, 70, 70))
        t2 = font_medium.render("Score: " + str(score), True, (255, 255, 255))
        t3 = font_small.render("Best:  " + str(high_score), True, (255, 220, 100))
        screen.blit(t1, t1.get_rect(center=(WIDTH//2, 230)))
        screen.blit(t2, t2.get_rect(center=(WIDTH//2, 305)))
        screen.blit(t3, t3.get_rect(center=(WIDTH//2, 360)))
        if score > 0 and score == high_score:
            rec = font_score.render("NEW RECORD!", True, (255, 220, 0))
            screen.blit(rec, rec.get_rect(center=(WIDTH//2, 400)))
        if is_mobile:
            draw_restart_btn()
        else:
            t4 = font_small.render("Press R to restart", True, (200, 200, 200))
            screen.blit(t4, t4.get_rect(center=(WIDTH//2, 445)))

    pygame.display.flip()

# =============================================================================
# UPDATE
# =============================================================================
def update(keys):
    global score, vitesse_orange, game_state, compt_heart, high_score
    global powerup, powerup_spawn_counter, double_shot_timer, flash_timer

    for o in oranges[:]:
        o["actor"].y += vitesse_orange * o["speed_mult"]
        if o["actor"].y > HEIGHT or o["actor"].colliderect(cowboy):
            compt_heart += 1
            oranges.remove(o)
            oranges.append(spawn_orange())
            flash_timer = FLASH_DURATION
            if life_lost_sound: life_lost_sound.play()
            add_float_text("-1 LIFE", WIDTH//2, HEIGHT//2, (255, 80, 80))
            if compt_heart == 1:   heart3.active = False
            elif compt_heart == 2: heart2.active = False
            elif compt_heart >= 3:
                heart1.active = False
                pygame.mixer.music.stop()
                if game_over_sound: game_over_sound.play()
                if game_over_voice: game_over_voice.play()
                if score > high_score: high_score = score
                game_state = STATE_GAMEOVER
                return

    powerup_spawn_counter += 1
    if powerup_spawn_counter >= POWERUP_INTERVAL and powerup is None:
        powerup = spawn_powerup_obj()
        powerup_spawn_counter = 0

    if powerup:
        powerup["rect"].y += 2
        if powerup["rect"].y > HEIGHT:
            powerup = None
        elif powerup["rect"].colliderect(cowboy.rect):
            if powerup["type"] == "life" and compt_heart > 0:
                compt_heart -= 1
                if compt_heart < 3: heart1.active = True
                if compt_heart < 2: heart2.active = True
                if compt_heart < 1: heart3.active = True
                add_float_text("+1 LIFE", powerup["rect"].centerx,
                               powerup["rect"].centery, (80, 255, 120))
            elif powerup["type"] == "double_shot":
                double_shot_timer = 360
                add_float_text("DOUBLE SHOT!", powerup["rect"].centerx,
                               powerup["rect"].centery, (255, 220, 0))
            if powerup_sound: powerup_sound.play()
            powerup = None

    if double_shot_timer > 0:
        double_shot_timer -= 1

    move_left  = keys[pygame.K_LEFT]  or touch_left
    move_right = keys[pygame.K_RIGHT] or touch_right

    if move_left:    cowboy.x -= 7
    elif move_right: cowboy.x += 7
    if cowboy.x < 20:    cowboy.x = 580
    elif cowboy.x > 580: cowboy.x = 20

    if (keys[pygame.K_SPACE] or touch_shoot) and not bullet.active:
        if shot_sound: shot_sound.play()
        bullet.x = cowboy.x
        bullet.y = cowboy.y - 20
        bullet.active = True
        if double_shot_timer > 0 and not bullet2.active:
            bullet2.x = cowboy.x + 22
            bullet2.y = cowboy.y - 20
            bullet2.active = True

    if bullet.active:
        bullet.y -= 10
        if bullet.y < 0:
            bullet.active = False
        else:
            for o in oranges[:]:
                if bullet.colliderect(o["actor"]):
                    spawn_particles(o["actor"].x, o["actor"].y)
                    pts = o["points"] * (2 if double_shot_timer > 0 else 1)
                    score += pts
                    add_float_text("+" + str(pts), o["actor"].x, o["actor"].y - 20)
                    vitesse_orange = min(vitesse_orange + 0.08, 12.0)
                    bullet.active = False
                    oranges.remove(o)
                    oranges.append(spawn_orange())
                    if score > 0 and score % 60 == 0 and len(oranges) < 3:
                        oranges.append(spawn_orange())
                    break

    if bullet2.active:
        bullet2.y -= 10
        if bullet2.y < 0:
            bullet2.active = False
        else:
            for o in oranges[:]:
                if bullet2.colliderect(o["actor"]):
                    spawn_particles(o["actor"].x, o["actor"].y)
                    pts = o["points"] * 2
                    score += pts
                    add_float_text("+" + str(pts), o["actor"].x, o["actor"].y - 20)
                    vitesse_orange = min(vitesse_orange + 0.08, 12.0)
                    bullet2.active = False
                    oranges.remove(o)
                    oranges.append(spawn_orange())
                    break

    update_particles()
    update_float_texts()

# =============================================================================
# MAIN LOOP
# =============================================================================
async def main():
    global game_state, difficulty
    global countdown_val, countdown_timer
    global touch_left, touch_right, touch_shoot
    global swipe_start_x, swipe_start_y, touch_finger_x

    resume_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 20, 160, 55)

    running = True
    while running:
        touch_shoot = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # ── KEYBOARD ──
            if event.type == pygame.KEYDOWN:
                if game_state == STATE_DIFFICULTY:
                    if event.key == pygame.K_1:
                        difficulty = "EASY";   reset_game()
                    elif event.key == pygame.K_2:
                        difficulty = "NORMAL"; reset_game()
                    elif event.key == pygame.K_3:
                        difficulty = "HARD";   reset_game()
                elif game_state == STATE_PLAYING:
                    if event.key == pygame.K_p:
                        game_state = STATE_PAUSED
                elif game_state == STATE_PAUSED:
                    if event.key == pygame.K_p:
                        game_state = STATE_PLAYING
                elif game_state == STATE_GAMEOVER:
                    if event.key == pygame.K_r:
                        if game_over_sound: game_over_sound.stop()
                        if game_over_voice: game_over_voice.stop()
                        game_state = STATE_DIFFICULTY

            # ── MOUSE / TOUCH ──
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos

                if game_state == STATE_DIFFICULTY:
                    if btn_easy.collidepoint(pos):
                        difficulty = "EASY";   reset_game()
                    elif btn_normal.collidepoint(pos):
                        difficulty = "NORMAL"; reset_game()
                    elif btn_hard.collidepoint(pos):
                        difficulty = "HARD";   reset_game()

                elif game_state == STATE_GAMEOVER:
                    if btn_restart.collidepoint(pos):
                        if game_over_sound: game_over_sound.stop()
                        if game_over_voice: game_over_voice.stop()
                        game_state = STATE_DIFFICULTY

                elif game_state == STATE_PAUSED:
                    if resume_rect.collidepoint(pos):
                        game_state = STATE_PLAYING

                elif game_state == STATE_PLAYING:
                    if is_mobile:
                        # Pause button
                        if btn_pause_mob.collidepoint(pos):
                            game_state = STATE_PAUSED
                        else:
                            # Start swipe tracking
                            swipe_start_x  = pos[0]
                            swipe_start_y  = pos[1]
                            touch_finger_x = pos[0]
                            touch_left     = False
                            touch_right    = False

            if event.type == pygame.MOUSEMOTION and is_mobile and swipe_start_x is not None:
                touch_finger_x = event.pos[0]
                dx = touch_finger_x - swipe_start_x
                if dx < -SWIPE_THRESHOLD:
                    touch_left  = True
                    touch_right = False
                elif dx > SWIPE_THRESHOLD:
                    touch_right = True
                    touch_left  = False
                else:
                    touch_left  = False
                    touch_right = False

            if event.type == pygame.MOUSEBUTTONUP and is_mobile:
                if swipe_start_x is not None and game_state == STATE_PLAYING:
                    dx = event.pos[0] - swipe_start_x
                    dy = event.pos[1] - swipe_start_y
                    dist = math.sqrt(dx*dx + dy*dy)
                    # Tap on cowboy = shoot
                    if dist < 20 and cowboy.rect.collidepoint(event.pos):
                        touch_shoot = True
                swipe_start_x  = None
                swipe_start_y  = None
                touch_finger_x = None
                touch_left     = False
                touch_right    = False

        # ── STATE MACHINE ──
        if game_state == STATE_DIFFICULTY:
            draw_difficulty_screen()

        elif game_state == STATE_COUNTDOWN:
            countdown_timer += 1
            if countdown_timer >= COUNTDOWN_DELAY:
                countdown_timer = 0
                countdown_val  -= 1
                if countdown_val < 0:
                    game_state = STATE_PLAYING
                    try: pygame.mixer.music.play(-1)
                    except: pass
            draw_countdown_screen()

        elif game_state == STATE_PAUSED:
            draw()
            draw_pause_overlay()

        elif game_state in (STATE_PLAYING, STATE_GAMEOVER):
            keys = pygame.key.get_pressed()
            if game_state == STATE_PLAYING:
                update(keys)
            draw()

        clock.tick(60)
        await asyncio.sleep(0)

    pygame.quit()

asyncio.run(main())
