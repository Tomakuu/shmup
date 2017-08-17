# Shmup game von Kida Can Code
# Shmup steht fuer shoot 'em up'
import pygame
import random
from os import path
import pandas as pd


WIDTH = 480
HEIGHT = 600
FPS = 60
POWERUPTIME = 3500

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0 ,0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)



pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SHMUP!")
clock = pygame.time.Clock()
font_name = pygame.font.match_font("arial")


img_folder = path.join(path.dirname(__file__), "img")
snd_folder = path.join(path.dirname(__file__), "snd")

maxspeed = 7
# load graphics
background = pygame.image.load(path.join(img_folder, "sterne.png")).convert()
background_rect = background.get_rect()
player_img = pygame.image.load(path.join(img_folder, "ship.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_folder, "laser.png")).convert()
mob_img_list = []
mob_name_list = ["m1.png", "m2.png", "m3.png", "m4.png", "m5.png", "m6.png",
                 "m7.png", "m8.png", "m9.png", "m10.png", "m11.png"]
for m in mob_name_list:
    i = pygame.image.load(path.join(img_folder, m)).convert()
    mob_img_list.append(i)
explotion_anim = {}
explotion_anim["lrg"] = []
explotion_anim["sml"] = []
explotion_anim["player"] = []
for i in range(9):
    filename = "regularExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    img_lrg = pygame.transform.scale(img, (75, 75))
    img_sml = pygame.transform.scale(img, (32, 32))
    explotion_anim["lrg"].append(img_lrg)
    explotion_anim["sml"].append(img_sml)
    filename = "sonicExplosion0{}.png".format(i)
    img = pygame.image.load(path.join(img_folder, filename)).convert()
    img.set_colorkey(BLACK)
    explotion_anim["player"].append(img)

powerup_img = {}
powerup_img["shield"] = pygame.image.load(path.join(img_folder, "shield_gold.png")).convert()
powerup_img["gun"] = pygame.image.load(path.join(img_folder, "bolt_gold.png")).convert()

#load sounds
bullet_sound = pygame.mixer.Sound(path.join(snd_folder, "laser.wav"))
shield_sound = pygame.mixer.Sound(path.join(snd_folder, "pow4.wav"))
gun_sound = pygame.mixer.Sound(path.join(snd_folder, "pow5.wav"))
hit_sound = pygame.mixer.Sound(path.join(snd_folder, "hit.wav"))
mob_sound = pygame.mixer.Sound(path.join(snd_folder, "explode.wav"))
kill_sound = pygame.mixer.Sound(path.join(snd_folder, "rumble1.ogg"))
pygame.mixer.music.load(path.join(snd_folder, "tgfcoder-FrozenJam-SeamlessLoop.ogg"))
pygame.mixer.music.set_volume(0.6)

def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    surf.blit(text_surface, text_rect)

def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

def draw_shield_bar(surf, pct, x, y):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 10
    fill = (pct/100) * BAR_LENGTH
    outline_bar = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_bar = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_bar)
    pygame.draw.rect(surf, WHITE, outline_bar, 2)

def draw_lives(surf, lives, x, y, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)

def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SHMUP!", 64, WIDTH/2, HEIGHT*0.25)
    draw_text(screen, "Pfeiltasten: Steuerung  Leertaste: Laser", 24, WIDTH/2, HEIGHT*0.5)
    draw_text(screen, "Start mit  's'  Taste", 24, WIDTH/2, HEIGHT*0.75)
    waiting = True
    pygame.display.flip()
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_s:
                    waiting = False

class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius, 1)
        self.rect.centerx = WIDTH/2
        self.rect.bottom = HEIGHT-10
        self.speedx = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()

    def update(self):
        # Verstecken nach Zerstörung
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 2000:
            self.hidden = False
            self.rect.centerx = WIDTH/2
            self.rect.bottom = HEIGHT-10
        # Ablauf der Gun Power Zeit
        if self.power >1 and  pygame.time.get_ticks() - self.power_timer > POWERUPTIME:
            self.power -= 1
            self.power_timer = pygame.time.get_ticks()
        # Bewegung und schiessen
        self.speedx = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT] and self.rect.left > 0:
            self.speedx = -5
        elif keystate[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.speedx = 5
        self.rect.x += self.speedx
        if keystate[pygame.K_SPACE] and player.hidden == False:
            self.shoot()

    def powerup(self):
        self.power += 1
        self.power_timer = pygame.time.get_ticks()

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot >= self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                b = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(b)
                bullets.add(b)
                bullet_sound.play()
            elif self.power >= 2:
                b1 = Bullet(self.rect.left, self.rect.centery)
                b2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(b1)
                all_sprites.add(b2)
                bullets.add(b1)
                bullets.add(b2)
                bullet_sound.play()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH/2, HEIGHT+500)

class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(mob_img_list)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = self.rect.width / 2.1
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius, 1)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(-200, -100)
        self.speedy = random.randrange(1, maxspeed)
        self.speedx = random.randrange(-3,3)
        self.rot = 0
        self.rot_speed = random.randint(-8, 8)
        self.last_update = pygame.time.get_ticks()

    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT+20 or self.rect.left < -60 or self.rect.right > WIDTH+60:
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -50)
            self.speedy = random.randrange(1, maxspeed)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10

    def update(self):
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explotion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explotion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explotion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explotion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(["shield", "gun"])
        self.image = powerup_img[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 5

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.kill()

# Game Loop
running = True
game_over = True
while running:
    clock.tick(FPS)

    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(8):
            newmob()
        pygame.mixer.music.play(loops=-1)
        score = 0
        speedscore = 0

    # Process Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


    # Update
    maxspeed = 7 + (speedscore//2500)
    if maxspeed >= 20:
        maxspeed = 20
    all_sprites.update()

    # abschuss
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += int(70 - hit.radius)
        speedscore += int(70 - hit.radius)
        mob_sound.play()
        expl = Explotion(hit.rect.center, "lrg")
        all_sprites.add(expl)
        newmob()
        if random.random() > 0.925:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)
            powerups.add(pow)

    # hit powerups
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == "shield":
            player.shield += random.randrange(10,30)
            shield_sound.play()
            if player.shield > 100:
                player.shield = 100
        elif hit.type == "gun":
            player.powerup()
            gun_sound.play()



    # kollision
    kill = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for k in kill:
        player.shield -= k.radius* 1.75
        if player.shield <= 0:
            kill_sound.play()
            death_exlpotion = Explotion(player.rect.center, "player")
            all_sprites.add(death_exlpotion)
            player.hide()
            player.lives -= 1
            player.shield = 100
            speedscore = 0
        else:
            hit_sound.play()
            expl = Explotion(k.rect.center, "sml")
            all_sprites.add(expl)

        newmob()

    if player.lives == 0 and not death_exlpotion.alive():
        game_over = True


    # Draw
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10)
    draw_shield_bar(screen, player.shield, 5, 5)
    draw_lives(screen, player.lives, WIDTH - 100, 5, player_mini_img)
    # *after* drawing everything
    pygame.display.flip()

pygame.quit()
