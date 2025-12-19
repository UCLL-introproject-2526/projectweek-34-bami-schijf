import pygame
import time
import sys
import os
from pygame.display import flip
from random import randint, choice, uniform
import math
import asyncio

MINIMAP_SIZE = (200, 150)  # breedte, hoogte van de minimap
MINIMAP_PADDING = 20        # afstand van schermrand
MINIMAP_BG_COLOR = (50, 50, 50)
MINIMAP_PLAYER_COLOR = (255, 255, 0)
MINIMAP_BORDER_COLOR = (200, 200, 200)

screen_size = (1024, 768)
highscore = (0, 0)

MINIMAP_RECT = pygame.Rect(
    MINIMAP_PADDING,
    screen_size[1] - MINIMAP_SIZE[1] - MINIMAP_PADDING,
    MINIMAP_SIZE[0],
    MINIMAP_SIZE[1]
)

pygame.init()
screen = pygame.display.set_mode(screen_size)

wave_images = [
    None,
    None,
    pygame.image.load("next_wave/wave 2.png").convert_alpha(),
    pygame.image.load("next_wave/wave 3.png").convert_alpha(),
    pygame.image.load("next_wave/wave 4.png").convert_alpha(),
    pygame.image.load("next_wave/you win.png").convert_alpha()
]

pygame.display.set_caption("Fixed Game")
clock = pygame.time.Clock() #clock objects voor framerate
font = pygame.font.SysFont("arialblack", 24) # voor HP, timer, wave progress

background_image = pygame.image.load("background/background-map 2 (snow).png").convert()
background_width, background_height = background_image.get_size()
scroll_x, scroll_y = 0, 0 # scroll offsets om camera te volgen

allenemywaves = {1: [0,0,10,0,0],2: [0,5,10,0,0],3: [5,10,15,0,0],4: [10,15,20,1,0], 5:[0,0,0,0,1]} # [fruit,labubu,zombie,boss, invisEnemy]
# allenemywaves = {1: [0,0,1,0,0],2: [0,1,0,0,0],3: [1,0,1,0,0],4: [0,0,0,1,0], 5:[0,0,0,0,1]} # [fruit,labubu,zombie,boss, invisEnemy]
enemies = []
punchitbox = None
global cangonextwave 
cangonextwave = True

# Preload veelgebruikte afbeeldingen om schijf-I/O tijdens gameplay te vermijden (voorkomt vastlopen)
LABUBU_PATHS = [
    "sprites/Labubu - sprite/Labubu -  pink.png",
    "sprites/Labubu - sprite/Labubu - dark blue.png",
    "sprites/Labubu - sprite/Labubu - gold.png",
    "sprites/Labubu - sprite/Labubu - green.png",
    "sprites/Labubu - sprite/Labubu - light blue.png",
    "sprites/Labubu - sprite/Labubu - orange.png",
    "sprites/Labubu - sprite/Labubu - purple.png",
]
FRUIT_PATHS = [
    "sprites/Fruit - sprite/Apple.png",
    "sprites/Fruit - sprite/Banana.png",
    "sprites/Fruit - sprite/Cherry.png",
    "sprites/Fruit - sprite/Orange.png",
]
try:
    LABUBU_RAW = [pygame.image.load(p).convert_alpha() for p in LABUBU_PATHS]
except Exception:
    LABUBU_RAW = []
try:
    FRUIT_RAW = [pygame.image.load(p).convert_alpha() for p in FRUIT_PATHS]
except Exception:
    FRUIT_RAW = []
try:
    ZOMBIE_RAW = pygame.image.load("sprites/Zombie - sprite/zombie.png").convert_alpha()
except Exception:
    ZOMBIE_RAW = None
try:
    BOSS_RAW = pygame.image.load("sprites/Labubu - sprite/Labubu - blue.png").convert_alpha()
except Exception:
    BOSS_RAW = None

# projectile assets
try:
    PEN_RAW = pygame.image.load("sprites/Projectile - sprite/pen.png").convert_alpha()
except Exception:
    PEN_RAW = None
try:
    PINE_RAW = pygame.image.load("sprites/Projectile - sprite/pineapple.png").convert_alpha()
except Exception:
    PINE_RAW = None
try:
    SHRAP_RAW = pygame.image.load("sprites/Projectile - sprite/shrapnel.png").convert_alpha()
except Exception:
    SHRAP_RAW = None

def distanceSquared(dx: int, dy:int):
    return dx**2 + dy**2

def getDir(selfCoords: tuple, playerCoords: tuple):
    dx, dy = playerCoords[0] - selfCoords[0], playerCoords[1] - selfCoords[1]
    size = distanceSquared(dx, dy)**(1/2)
    return (dx/size, dy/size)


class Player:
    def __init__(self):
        self.draw_offset_x = 0
        self.__maxHp = 15
        self.__health = self.__maxHp
        self.base_speed = 3 # basissnelheid, wordt aangepast bij diagonale bewegingen (moet dit wel?)
        self.speed = self.base_speed
        self.width = 60
        self.height = 100
        self.__weapons = set()
        # Player is always at the center of the screen
        self.screen_x = screen_size[0] // 2 - self.width // 2
        self.screen_y = screen_size[1] // 2 - self.height // 2
        # World position tracks where the player is in the game world
        self.world_x = background_width // 2 - self.width //2
        self.world_y = background_height // 2 - self.height // 2
        self.sword_x = self.screen_x + self.width
        self.sword_y = self.screen_y - 5

        global scroll_x, scroll_y
        scroll_x = max(0, min(self.world_x - screen_size[0] // 2, background_width - screen_size[0]))
        scroll_y = max(0, min(self.world_y - screen_size[1] // 2, background_height - screen_size[1]))


        self.direction = "right"
        self.is_moving = False
        self.walk_frame = 0 # voor switchen tussen walking sprites
        self.walk_timer = 0 # telt frames om walk_frame te togglen

        self.sprites = {
            "left": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - left.png").convert_alpha(),
                (self.width, self.height)
            ),

            "left_walking": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - left walking.png").convert_alpha(),
                (self.width, self.height)
            ),

            "right": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - right.png").convert_alpha(),
                (self.width, self.height)
            ),

            "right_walking": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - right walking.png").convert_alpha(),
                (self.width, self.height)    
            ),

            "left_punch": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - left punch.png").convert_alpha(),
                (self.width, self.height)
            ),
            "right_punch": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - right punch.png").convert_alpha(),
                (self.width, self.height)
            ),
        }

        self.sword_image = pygame.image.load("sprites/Projectile - sprite/sword.png").convert_alpha()
        self.sword_image = pygame.transform.rotate(self.sword_image, -90)

        self.sword_width = 130
        self.sword_height = 90

        self.sword_image = pygame.transform.scale(self.sword_image, (self.sword_width, self.sword_height)
)


        self.image = self.sprites["right"] # start sprite
        self.punching = False   # punch status
        self.punch_timer = 0    # countdown voor punch animatie
        self.alive_start = None # timer start voor hoe lang speler alive is
        self.alive_end = None   # timer einde bij dood

    def getNearestEnemy(self, enemies: list):
        min = math.inf
        nearest = None
        for enemy in enemies:
            if enemy.hostile:
                temp = distanceSquared(self.world_x - enemy.world_x, self.world_y - enemy.world_y)
                if temp < min:
                    min = temp
                    nearest = enemy
        return nearest

    def draw(self, screen):
        self.draw_shadow(screen)
        # Always draw player at the center of the screen
        screen.blit(
            self.image,
            (self.screen_x + self.draw_offset_x, self.screen_y)
        )
        if self.punching and self.has_weapon("PPAP"):
            sword = self.sword_image

            if self.direction == "left":
                sword = pygame.transform.flip(sword, True, False)

            # position sword relative to player
            sword_x = self.screen_x + self.width
            sword_y = self.screen_y - 5

            if self.direction == "left":
                sword_x -= self.sword_width + self.width

            screen.blit(sword, (sword_x, sword_y))



    def draw_shadow(self, screen):
        shadow_width = self.width * 0.8
        shadow_height = self.height * 0.25
        shadow_x = self.screen_x + (self.width - shadow_width) / 2
        shadow_y = self.screen_y + self.height - shadow_height * 0.6


        shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), shadow.get_rect())  # 100 = alpha
        screen.blit(shadow, (shadow_x, shadow_y))
    
    def get_maxHp(self):
        return self.__maxHp
    def get_hp(self):
        return self.__health

    def take_damage(self, id: int):
        # damage variabele per enemy type
        if id == 1:
            dmg = 1
        elif id == 2 or id == 3:
            dmg = 2
        else:
            dmg = 5
        self.__health -= dmg
        if self.__health < 0:
            self.__health = 0
    
    def regen_hp(self, regen):
        # regeneratie, limiet op maxHP
        self.__health += regen
        if self.__health > self.__maxHp:
            self.__health = self.__maxHp

    def punch(self, invincible):
        if not self.punching:
            # start punch animatie
            print("punch")
            if self.direction == "right":
                self.image = self.sprites["right_punch"]
            else:
                self.image = self.sprites["left_punch"]
            self.punching = True
            self.punch_timer = 30   # aantal frames dat punch actief is
            global punch_sound
            punch_sound.play()
            
            return 30   # geeft frames terug voor invincible timer
        return invincible # als al punching, verander niets 
    
    def up(self):
        global scroll_y
        # verplaats de speler in wereldcoördinaten omhoog
        self.world_y -= self.speed
        # beperk positie binnen kaart, voorkomt dat speler te ver naar boven gaat
        self.world_y = max(screen_size[1] // 2, min(self.world_y, background_height - self.height))
        # update scroll zodat camera volgt
        scroll_y = max(0, min(self.world_y - screen_size[1] // 2, background_height - screen_size[1]))

    def down(self):
        global scroll_y
        # verplaats de speler in de wereldcoördinaten naar beneden
        self.world_y += self.speed
        # voorkomt dat speler buiten de onderkant gaat
        self.world_y = min(background_height - screen_size[1] // 2, min(self.world_y, background_height - self.height))
        scroll_y = max(0, min(self.world_y - screen_size[1] // 2, background_height - screen_size[1]))

    def left(self):
        global scroll_x
        # verplaats speler naar links in wereldcoördinaten 
        self.world_x -= self.speed
        self.world_x = max(screen_size[0] // 2, min(self.world_x, background_width - self.width))
        # update scroll
        scroll_x = max(0, min(self.world_x - screen_size[0] // 2, background_width - screen_size[0]))

    def right(self):
        global scroll_x
        # verplaats de speler naar rechts in wereldcoördinaten 
        self.world_x += self.speed
        self.world_x = min(background_width - screen_size[0] // 2 , min(self.world_x, background_width - self.width))
        scroll_x = max(0, min(self.world_x - screen_size[0] // 2, background_width - screen_size[0]))

    def look_left(self):
        self.direction = "left"

    def look_right(self):
        self.direction = "right"

    def add_weapon(self, weapon: str):
        self.__weapons.add(weapon)
    def has_weapon(self, weapon: str):
        return weapon in self.__weapons

    def update_image(self):
        punch_width = 75
        punch_height = 102

        if self.punching:
            # schaal punch sprite
            self.image = pygame.transform.scale(self.sprites[f"{self.direction}_punch"], (punch_width, punch_height))

            # CENTREER zowel links als rechts
            self.draw_offset_x = (self.width - punch_width) // 2  # halve verschil, zodat centreren
        else:
            self.draw_offset_x = 0
            if self.is_moving:
                self.walk_timer += 1
                if self.walk_timer >= 10:
                    self.walk_timer = 0
                    self.walk_frame = 1 - self.walk_frame
                if self.walk_frame == 0:
                    self.image = self.sprites[self.direction]
                else:
                    self.image = self.sprites[f"{self.direction}_walking"]
            else:
                self.image = self.sprites[self.direction]

    
    def get_nearest_enemy(self, enemies):
        if  enemies == []:
            return None

        nearest = None
        min_dist = math.inf
        for enemy in enemies:
            if enemy.hostile:
                dx = enemy.world_x - self.world_x
                dy = enemy.world_y - self.world_y
                dist = dx**2 + dy**2
                if dist < min_dist:
                    min_dist = dist
                    nearest = enemy
        return nearest

    def get_rect(self):
        return pygame.Rect(self.screen_x, self.screen_y, self.width, self.height)
    
    def get_rect_sword(self):
        if not self.has_weapon("PPAP"):
            return pygame.Rect(0, 0, 0, 0)
        # self.sword coords aangepast in draw()
        world_x = self.sword_x + scroll_x
        world_y = self.sword_y + scroll_y

        return pygame.Rect(world_x, world_y, self.sword_width, self.sword_height)

    def get_world_rect(self):
        return pygame.Rect(self.world_x, self.world_y, self.width, self.height)


class hitBox:
    def __init__(self, duration, size, player: Player):
        self.startTime = time.time()
        self.duration = duration
        self.active = True
        self.x = 20  # even gehardcode want de player heeft geen x en y coordinaten
        self.y = 20
        self.player = player
        self.size = size

    def update(self, dt):
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (self.player.screen_x, self.player.screen_y, self.size[0], self.size[1]),
            100
        )
        self.time_left -= dt
        if self.time_left <= 0:
            self.active = False
            self.player.look_right()
    
    def get_rect(self):
        if self.player.direction == "right":
            x = self.player.world_x + self.player.width
        else:
            x = self.player.world_x - self.size[0]

        y = self.player.world_y + self.player.height // 3

        return pygame.Rect(x, y, self.size[0], self.size[1])
    
class Npc:
    def __init__(self):
        self.world_x, self.world_y = randint(screen_size[0]//2, background_width-screen_size[0]//2), randint(screen_size[1]//2, background_height-screen_size[1]//2)
        self.width, self.height = 45, 60
        self.base_speed = 3
        self.speed = self.base_speed
        self.shrink_width = 22.5
        self.shrink_height = 45
        self.hostile = True
        self.inv = False   

    def draw(self, screen):
        if self.hostile:
            screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
            screen.blit(self.image, (screen_x, screen_y))

    def draw_shadow(self, screen):
        shadow_width = self.width * 0.8
        shadow_height = self.height * 0.25
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        shadow_x = screen_x + (self.width - shadow_width) / 2
        shadow_y = screen_y + self.height - shadow_height * 0.6  # pas hier eventueel offset aan
        shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,100), shadow.get_rect())
        screen.blit(shadow, (shadow_x, shadow_y))

    def trace(self, player: Player):
        if self.hostile:
            m = getDir((self.world_x + self.width // 2, self.world_y), (player.world_x, player.world_y - self.height // 2))
            self.world_x += m[0] * self.speed
            self.world_y += m[1] * self.speed

    def get_screen_pos(self, scroll_x, scroll_y):
        return (self.world_x - scroll_x, self.world_y - scroll_y)

    def get_rect(self):
        return pygame.Rect(
            self.world_x + self.shrink_width // 2,
            self.world_y + self.shrink_height // 2,
            self.width - self.shrink_width,
            self.height - self.shrink_height
        )

    def takedamage(self,amount):
        if not self.inv:
            if self.health - amount <= 0 : 
                self.health = 0
            else:
                self.health -= amount

class Projectile():
    def __init__(self,player : Player,enemy : Npc):
        
        self.world_x = player.world_x - player.width // 2
        self.world_y = player.world_y - player.height // 2
        self.width = 75
        self.height = 100
        self.dir = getDir((self.world_x + player.width // 2, self.world_y + self.height // 2), (enemy.world_x + enemy.width // 2, enemy.world_y + enemy.height // 2))
        print(self.dir)
        # gebruik vooraf geladen `PEN_RAW` als beschikbaar
        if PEN_RAW:
            self.image = pygame.transform.scale(PEN_RAW, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255,255,0), (self.width//2, self.height//2), min(self.width,self.height)//2)

        self.angle = math.degrees(math.atan2(-self.dir[1], self.dir[0])) + 90
        self.image = pygame.transform.rotate(self.image,self.angle)
        self.lifespan = 40
        self.speed = 10
        self.hasCollided = False
        self.isPen = True
        self.isPineapple = False
        self.isShrapnel = False

    def goDir(self):
        self.world_x += self.speed * self.dir[0]
        self.world_y += self.speed * self.dir[1]
        self.lifespan -= 1 
    
    def checkforlife(self):
        if self.lifespan <= 0 or self.hasCollided:
            return False
        return True
    
    def get_screen_pos(self):
        return (self.world_x - scroll_x, self.world_y - scroll_y)


    def draw(self, screen):
        screen_x, screen_y = self.get_screen_pos()
        screen.blit(self.image, (screen_x, screen_y))
    
    def handle(self):
        self.goDir()
        return self.checkforlife()
    
    def get_rect(self):
        return pygame.Rect(
            self.world_x,
            self.world_y,
            self.width,
            self.height
    )

class Pineapple(Projectile):
    def __init__(self, player, enemy):
        super().__init__(player, enemy)
        self.isPen = False
        self.isPineapple = True
        if PINE_RAW:
            self.image = pygame.transform.scale(PINE_RAW, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255,165,0), (self.width//2, self.height//2), min(self.width,self.height)//2)

        self.angle = math.degrees(math.atan2(-self.dir[1], self.dir[0])) + 90
        self.image = pygame.transform.rotate(self.image,self.angle)

    def explode(self):
        res = []
        for i in range(8):
            res.append(Shrapnel((self.world_x - self.width // 2, self.world_y + self.height // 2), math.radians(i*360/8)))
        return res

class Shrapnel(Projectile):
    def __init__(self, coords: tuple, angle: float):
        self.dir = (math.cos(angle), math.sin(angle))
        self.world_x = coords[0]
        self.world_y = coords[1]
        self.lifespan = 10
        self.width = 5
        self.height = 5
        self.speed = 10
        if SHRAP_RAW:
            self.image = pygame.transform.scale(SHRAP_RAW, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (200,200,200), self.image.get_rect())
        self.isPen = False
        self.isPineapple = False
        self.isShrapnel = True
        self.hasCollided = False

class invisEnemy(Npc):
    def __init__(self):
        super().__init__()
        self.width, self.height = 0,0
        self.hostile = False
        self.health = math.inf

class Labubu(Npc):
    def __init__(self):
        super().__init__()
        self.speed = 4
        # gebruik vooraf geladen Labubu-afbeeldingen
        if LABUBU_RAW:
            src = choice(LABUBU_RAW)
            self.image = pygame.transform.scale(src, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.ellipse(self.image, (255,192,203), self.image.get_rect())
        self.shrink_width = 30
        self.shrink_height = 40
        self.health = 305
        self.id = 3

class Zombie(Npc):
    def __init__(self):
        super().__init__()
        self.speed = 2.5
        if ZOMBIE_RAW:
            self.image = pygame.transform.scale(ZOMBIE_RAW, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (0,128,0), self.image.get_rect())
        self.shrink_width = 30
        self.shrink_height = 40
        self.health = 55
        self.id = 1

class Fruit(Npc):
    def __init__(self):
        super().__init__()
        self.speed = 3.5
        self.health = 155
        self.id = 2
        self.width = 70
        self.shrink_width = 5
        self.shrink_height = 10
        if FRUIT_RAW:
            src = choice(FRUIT_RAW)
            self.image = pygame.transform.scale(src, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255,0,0), (self.width//2, self.height//2), min(self.width,self.height)//2)

class Boss(Npc):
    def __init__(self):
        super().__init__()
        self.width = 150
        self.height = 200
        self.world_x = background_width // 2 - self.width
        self.world_y = background_height // 8
        if BOSS_RAW:
            self.image = pygame.transform.scale(BOSS_RAW, (self.width, self.height))
        else:
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (0,0,255), self.image.get_rect())
        self.shrink_width = 80
        self.shrink_height = 120
        self.health = 5000
        self.id = 4

class Text:
    def __init__(self, path="background/tutorial gamecontrols.png"):
        self.width = 500
        self.height = 200
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] // 2) + 150
        self.y = (screen_size[1] // 2) + 150

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

def renderFrame(screen, player: Player, npcs: list, hearts: list, hit: hitBox, projectiles: list, text=None):
    screen.blit(background_image, (0, 0), area=pygame.Rect(scroll_x, scroll_y, screen_size[0], screen_size[1]))
    
    drawables = npcs[:] # lijst kopie
    drawables.sort(key=lambda obj: obj.world_y + obj.height)
    
    for obj in drawables:
        if hasattr(obj, "draw_shadow"):
            obj.draw_shadow(screen)

    for obj in drawables:
        if obj.hostile:         # exclude invisible enemy
            obj.draw(screen)
    for heart in hearts:
        heart.draw(screen, scroll_x, scroll_y)
    for projectile in projectiles:
        projectile.draw(screen)
    player.draw(screen)
    if text:
        text.draw(screen)
    if hit:
        hit.draw(screen)

def draw_health(screen, player: Player):
    padding = 8

    hp_text = font.render(
        f"HP: {player.get_hp()} / {player.get_maxHp()}",
        True,
        (220,30,30)
    )

    bg_rect = hp_text.get_rect(topleft=(20,20))
    bg_rect.inflate_ip(padding*2, padding*2)

    pygame.draw.rect(screen, (180,180,180), bg_rect, border_radius=6)

    text_rect = hp_text.get_rect(center=bg_rect.center)
    screen.blit(hp_text, text_rect)

def draw_wave_progress(screen, kills, total):
    if total <= 0:
        progress = 0
    else:
        progress = int(kills / total * 100)
    
    progress_text = font.render(f"Wave Progress: {progress}%", True, (255, 255, 255))
    bg_rect = progress_text.get_rect(topleft=(15, 80)) 
    bg_rect.inflate_ip(8, 8)
    pygame.draw.rect(screen, (50, 50, 50), bg_rect, border_radius=6)
    text_rect = progress_text.get_rect(center=bg_rect.center)
    screen.blit(progress_text, text_rect)

def draw_timer(screen, player: Player, curr_wave, paused=False, pause_start_time=None):
    global highscore
    if player.alive_start is None:
        elapsed = 0
    else:
        if player.get_hp() <= 0 or curr_wave == 5:
            # sla verstreken tijd op
            if player.alive_end is None:
                player.alive_end = time.time()
            
            elapsed_time = int(player.alive_end - player.alive_start)  # altijd definiëren
            
            # Alleen bij hogere wave, of zelfde wave maar langere tijd
            if curr_wave > highscore[0] or (curr_wave == highscore[0] and elapsed_time > highscore[1]):
                highscore = (curr_wave, elapsed_time)
                with open("highscore.txt", "w") as f:
                    f.write(f"{highscore[0]},{highscore[1]}")
            
            elapsed = elapsed_time
        else:
            now = time.time()
            if paused and pause_start_time is not None:
                elapsed = int(pause_start_time - player.alive_start)
            else:
                elapsed = int(now - player.alive_start)

    mins = elapsed // 60
    secs = elapsed % 60
    timer_text = f"{mins:02}:{secs:02}"
    text_surf = font.render(timer_text, True, (255, 255, 255))
    bg_rect = text_surf.get_rect(center=(screen_size[0] // 2, 30))
    bg_rect.inflate_ip(8, 8)
    pygame.draw.rect(screen, (0, 0, 0), bg_rect, border_radius=6)
    text_pos = text_surf.get_rect(center=bg_rect.center)
    screen.blit(text_surf, text_pos)


def draw_highscore_left(screen, highscore):
    wave, elapsed = highscore
    mins = elapsed // 60
    secs = elapsed % 60

    line1 = font.render(f"Fastest time: {mins:02}:{secs:02}", True, (255, 255, 255))
    line2 = font.render(f"to reach wave {wave}", True, (255, 255, 255))

    # bepaal achtergrondgrootte
    width = max(line1.get_width(), line2.get_width()) + 16  # padding
    height = line1.get_height() + line2.get_height() + 16

    # linker uitlijning, net als HP-balk
    bg_rect = pygame.Rect(10, 130, width, height)  # x=15 uitgelijnd met HP-balk, y=80 iets eronder

    pygame.draw.rect(screen, (50, 50, 50), bg_rect, border_radius=6)

    # teken tekst linksboven op achtergrond
    screen.blit(line1, (bg_rect.x + 8, bg_rect.y + 8))
    screen.blit(line2, (bg_rect.x + 8, bg_rect.y + 8 + line1.get_height()))


def draw_boss_hp(screen, enemies):
    # zoek levende boss
    boss = None
    for e in enemies:
        if isinstance(e, Boss):
            boss = e
            break

    if boss is None:
        return  # geen boss → niets tekenen

    text = font.render(f"BOSS HP: {boss.health}", True, (255, 255, 255))

    padding = 8
    bg_rect = text.get_rect(topleft=(18, 233))  # onder highscore
    bg_rect.inflate_ip(padding * 2, padding * 2)

    pygame.draw.rect(screen, (55, 55, 55), bg_rect, border_radius=6)
    screen.blit(text, text.get_rect(center=bg_rect.center))


def end_game():
    return Text("background/game_over.png")

def restart_button_rect():
    return pygame.Rect(
        screen_size[0] // 2 - 100,
        screen_size[1] // 2 + 160,
        200,
        50
    )

def continue_button_rect():
    return pygame.Rect(
        screen_size[0] // 2 - 100,
        screen_size[1] // 2 + 240,
        200,
        50
    )

def main_menu_button_rect():
    return pygame.Rect(
        screen_size[0] // 2 - 100,
        screen_size[1] // 2 + 80,
        200,
        50
    )

def startnewave(currentwave, hearts):
    enemies = []
    multi = 3
    fruit,labubu,zombie,boss,invis_enemy = allenemywaves.get(currentwave,[randint(1,10)+currentwave * multi ,randint(1,10)+currentwave * multi ,randint(1,10)+currentwave * multi,currentwave-6 ,0])
    for _ in range(fruit):
        enemies.append(Fruit())
    for _ in range(labubu):
        enemies.append(Labubu())
    for _ in range(zombie):
        enemies.append(Zombie())
    for _ in range(boss):
        enemies.append(Boss())
    for _ in range(invis_enemy):
        enemies.append(invisEnemy())
    margin = screen_size[0] // 2

    # twee regen hartjes bij per wave
    for _ in range(2):
        x = randint(margin, background_width - margin - 32)
        y = randint(margin, background_height - margin - 32)
        hearts.append(Heart(x, y))
    
    return enemies


async def startnewave_async(currentwave, hearts, batch=10):
    enemies = []
    multi = 3
    fruit,labubu,zombie,boss,invis_enemy = allenemywaves.get(currentwave,[randint(1,10)+currentwave * multi ,randint(1,10)+currentwave * multi ,randint(1,10)+currentwave * multi,currentwave-6 ,0])

    # helper om vijanden incrementeel aan te maken om blokkering te vermijden
    def create(kind):
        if kind == 'fruit':
            return Fruit()
        if kind == 'labubu':
            return Labubu()
        if kind == 'zombie':
            return Zombie()
        if kind == 'boss':
            return Boss()
        if kind == 'invis':
            return invisEnemy()

    counts = [('fruit', fruit), ('labubu', labubu), ('zombie', zombie), ('boss', boss), ('invis', invis_enemy)]
    created = 0
    for kind, cnt in counts:
        for _ in range(cnt):
            enemies.append(create(kind))
            created += 1
            if created % batch == 0:
                    # verwerk events en geef controle terug zodat de browser niet bevriest
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        remove_highscore_file()
                        pygame.quit()
                        sys.exit()
                await asyncio.sleep(0)

    margin = screen_size[0] // 2
    # twee regen hartjes bij per wave
    for _ in range(2):
        x = randint(margin, background_width - margin - 32)
        y = randint(margin, background_height - margin - 32)
        hearts.append(Heart(x, y))

    return enemies


async def main_menu():
    menu_clock = pygame.time.Clock()
    btn_font = pygame.font.SysFont("arialblack", 36)
    play_rect = pygame.Rect(screen_size[0] // 2 - 100, screen_size[1] // 2 - 40, 200, 50)
    quit_rect = pygame.Rect(screen_size[0] // 2 - 100, screen_size[1] // 2 + 30, 200, 50)
    # try to load background image for main menu; fallback to solid fill
    try:
        menu_bg = pygame.image.load("background/Main menu.png").convert()
        menu_bg = pygame.transform.smoothscale(menu_bg, screen_size)
    except Exception:
        menu_bg = None

    while True:
        mpos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                remove_highscore_file()
                pygame.quit()
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if play_rect.collidepoint(event.pos):
                    return True
                if quit_rect.collidepoint(event.pos):
                    remove_highscore_file()
                    pygame.quit()
                    return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    remove_highscore_file()
                    pygame.quit()
                    return False
                if event.key == pygame.K_RETURN:
                    return True

        # background
        if menu_bg:
            screen.blit(menu_bg, (0, 0))
        else:
            screen.fill((20, 20, 40))

        # draw semi-transparent buttons so they blend with background
        for rect, label in ((play_rect, "PLAY"), (quit_rect, "QUIT")):
            hover = rect.collidepoint(mpos)

            # Button achtergrond
            btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    
            # Normale achtergrond (donkergrijs semi-transparant)
            btn_surf.fill((10, 10, 10, 140))
    
            # Hoverkleur alleen binnen afgeronde hoeken
            if hover:
                hover_color = (196, 67, 45, 200)  # oranje met alpha 200
                pygame.draw.rect(btn_surf, hover_color, btn_surf.get_rect(), border_radius=10)
    
            # Rand van de knop
            pygame.draw.rect(btn_surf, (255, 255, 255, 60), btn_surf.get_rect(), 2, border_radius=10)

            # Tekst altijd wit
            txt = btn_font.render(label, True, (255, 255, 255))
            screen.blit(btn_surf, rect.topleft)
            screen.blit(txt, txt.get_rect(center=rect.center))

        pygame.display.flip()
        # gebruik een korte async-vriendelijke sleep wanneer het in pygbag draait
        try:
            await asyncio.sleep(1/60)
        except Exception:
            # fallback voor synchrone uitvoering
            menu_clock.tick(60)


def draw_menu_button(surface, rect, hover=False):
    bg = (210, 210, 210) if not hover else (190, 190, 190)
    line_color = (30, 30, 30)
    pygame.draw.rect(surface, bg, rect, border_radius=8)
    # draw three horizontal lines for a cleaner 'menu' icon
    cx, cy = rect.center
    line_w = int(rect.width * 0.45)
    spacing = 6
    start_x = cx - line_w // 2
    for offset in (-spacing, 0, spacing):
        y = cy + offset
        pygame.draw.line(surface, line_color, (start_x, y), (start_x + line_w, y), 3)

def remove_highscore_file():
    # Verwijder het highscore bestand als het bestaat
    if os.path.exists("highscore.txt"):
        os.remove("highscore.txt")


MINIMAP_BG = pygame.transform.smoothscale(background_image, MINIMAP_SIZE)
MINIMAP_UPDATE_INTERVAL = 8
minimap_timer = 0

def draw_minimap(screen, player: Player, npcs: list, hearts: list):
    # linkeronderhoek van de map
    x = MINIMAP_PADDING
    y = screen_size[1] - MINIMAP_SIZE[1] - MINIMAP_PADDING

    # rechthoek van minimap (positie + grootte)
    minimap_rect = pygame.Rect(x, y, MINIMAP_SIZE[0], MINIMAP_SIZE[1])
    # achtergrond van minimap tekenen
    pygame.draw.rect(screen, MINIMAP_BG_COLOR, minimap_rect, border_radius=4)
    # rand rond de minimap tekenen
    pygame.draw.rect(screen, MINIMAP_BORDER_COLOR, minimap_rect, 2, border_radius=4)
    screen.blit(MINIMAP_BG, (x, y))

    # schaalfactor: wereld -> minimap
    scale_x = MINIMAP_SIZE[0] / background_width
    scale_y = MINIMAP_SIZE[1] / background_height

    # alle npc's (enemies) op de minimap tekenen
    for npc in npcs:
        # enkel 'vijandige' npcs tonen (invis niet tonen)
        if npc.hostile:
            # wereldpositie omzetten naar minimap-positie
            mini_x = x + int(npc.world_x * scale_x)
            mini_y = y + int(npc.world_y * scale_y)

            # boss onderscheiden van gewone enemies
            if isinstance(npc, Boss):
                radius = 6  # groter voor Boss
                color = (0, 0, 255)  # blauw
            else:
                radius = 3  # normale vijanden
                color = (0, 200, 0)  # groen

            pygame.draw.circle(screen, color, (mini_x, mini_y), radius)

    # hearts op de minimap tekenen
    for heart in hearts:
        mini_x = x + int(heart.world_x * scale_x)
        mini_y = y + int(heart.world_y * scale_y)
        # hearts zijn rood en klein
        pygame.draw.circle(screen, (255, 0, 0), (mini_x, mini_y), 3)

    # speler positie
    px = x + int(player.world_x * scale_x)
    py = y + int(player.world_y * scale_y)
    pygame.draw.circle(screen, MINIMAP_PLAYER_COLOR, (px, py), 5)



class Snowflake:
    def __init__(self):
        self.x = randint(0, screen_size[0]) # start x-positie willekeurig over de volledige schermbreedte
        self.y = randint(-screen_size[1], 0) # start y-positie boven het scherm
        self.radius = randint(2, 6)  # max grootte vergelijkbaar met speler
        self.speed = uniform(1, 3) #valsnelheid van sneeuw, kleine variaties voor realistisch effect

    def update(self, player_dx=0, player_dy=0):
        self.y += self.speed # sneeuwvlok valt verticaal naar beneden
        self.x -= player_dx * 1.7 # parallax-effect, speler beweegt tegen de sneeuw in
        self.y -= player_dy * 1.7 # parallax-effect, speler beweegt tegen de sneeuw in
        if self.y > screen_size[1]:
            self.y = randint(-50, -10) # opnieuw boven het scherm
            self.x = randint(0, screen_size[0])
            self.radius = randint(2, 6) # nieuwe grootte
            self.speed = uniform(1, 3)  # nieuwe snelheid

    def draw(self, screen, minimap_rect):
        # alleen tekenen als het niet over de minimap valt
        if not minimap_rect.collidepoint(self.x, self.y):
            pygame.draw.circle(screen, (255,255,255), (int(self.x), int(self.y)), self.radius)

class Heart:
    def __init__(self, x, y):
        self.world_x = x
        self.world_y = y

        self.amount = 1

        self.width = 32
        self.height = 32

        self.image = pygame.image.load("sprites/Heart - sprite/heart.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def draw(self, screen, scroll_x, scroll_y):
        screen.blit(
            self.image,
            (self.world_x - scroll_x, self.world_y - scroll_y)
        )

    def get_rect(self):
        return pygame.Rect(
            self.world_x,
            self.world_y,
            self.width,
            self.height
    )

async def main():
    # audio may be unavailable in browser (pygbag). Fall back to dummy sounds.
    audio_available = True
    class DummySound:
        def play(self, *a, **k):
            return None

    try:
        pygame.mixer.init()
        pygame.mixer.music.load('sounds/background.ogg')
        pygame.mixer.music.play(-1, 0, 0)
        pygame.mixer.music.set_volume(0.25)
        dmg_sound = pygame.mixer.Sound('sounds/damage.ogg')
        tick_sound = pygame.mixer.Sound('sounds/tick.ogg')
        game_over = pygame.mixer.Sound("sounds/gameover.ogg")
        regen_sound = pygame.mixer.Sound('sounds/regen.ogg')
        global punch_sound
        punch_sound = pygame.mixer.Sound('sounds/punch.ogg')
    except Exception:
        audio_available = False
        dmg_sound = DummySound()
        tick_sound = DummySound()
        game_over = DummySound()
        regen_sound = DummySound()
        punch_sound = DummySound()

    global highscore
    mute_img = pygame.image.load("background/mute.png").convert_alpha() #mute audio knop
    mute_img = pygame.transform.scale(mute_img, (40, 40))
    music_button_rect = pygame.Rect(screen_size[0] - 60, 20, 40, 40)
    menu_button_rect = pygame.Rect(screen_size[0] - 110, 20, 40, 40)
    small_font = pygame.font.SysFont("arialblack", 20)
    music_on = True
    foo = True
    flash_timer = 0
    flash_duration = 3
    player = Player()
    text = Text()
    invincible = False
    stunned = False
    game_start = False
    global cangonextwave
    currentwave = 1
    kills_this_wave = 0  # aantal kills in de huidige wave
    total_enemies_in_wave = sum(allenemywaves.get(currentwave))  # totaal aantal enemies in deze wave
    hearts = []  # start lege lijst
    projectiles = []
    currentwave = 1
    enemies = await startnewave_async(currentwave, hearts)
    pen_time = 0
    pine_time = 0
    snowflakes = [Snowflake() for _ in range(100)]
    snow_surface = pygame.Surface(screen_size, pygame.SRCALPHA)
    # Lees highscore bij start
# Lees highscore bij start
    try:
        with open("highscore.txt", "r") as f:
            parts = f.read().split(",")
            highscore = (int(parts[0]), int(parts[1]))  # (wave, tijd)
    except FileNotFoundError:
        highscore = (0, 0)



    async def show_wave_overlay(wave_number, duration=2):
        if 1 <= wave_number < len(wave_images):
            overlay = wave_images[wave_number]
            overlay_rect = overlay.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2 - 50))
            # Draw and keep pumping events while waiting so browser stays responsive
            end_time = asyncio.get_event_loop().time() + duration * 0.35
            while asyncio.get_event_loop().time() < end_time:
                # redraw overlay so the browser doesn't consider the page unresponsive
                screen.blit(overlay, overlay_rect)
                pygame.display.flip()
                # process events to keep browser/SDL responsive
                for ev in pygame.event.get():
                    if ev.type == pygame.QUIT:
                        remove_highscore_file()
                        pygame.quit()
                        sys.exit()
                await asyncio.sleep(0.016)

    running = True
    paused = False
    pause_start_time = None

    current_wave = 1
    while running:

        player_dx = 0
        player_dy = 0

        if paused:
            # Render huidig frame
            renderFrame(screen, player, enemies, hearts, punchitbox, projectiles, text)
            # tekst en interface elementen behouden, anders vallen die weg wanneer op pauze
            draw_health(screen, player) # hp 
            draw_wave_progress(screen, kills_this_wave, total_enemies_in_wave) # wave progress
            draw_highscore_left(screen, highscore) # toon highscore
            draw_timer(screen, player, currentwave, paused, pause_start_time) # toon timer (! stop tijdens pauze)
            draw_minimap(screen, player, enemies, hearts) # toon minimap
            draw_boss_hp(screen, enemies)

            # Teken mute-knop ook tijdens pauze + menu knop
            mpos = pygame.mouse.get_pos()
            hover = menu_button_rect.collidepoint(mpos)
            draw_menu_button(screen, menu_button_rect, hover=hover)
            btn_color = (100, 220, 100) if music_on else (220, 100, 100)
            pygame.draw.rect(screen, btn_color, music_button_rect, border_radius=6)
            screen.blit(mute_img, (music_button_rect.x, music_button_rect.y))

            # Overlay "PAUSED"
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            screen.blit(pause_text, pause_text.get_rect(center=(screen_size[0] // 2, screen_size[1] // 2)))

            pygame.display.flip() # update scherm
            clock.tick(60) #framerate behouden

            # Event-loop voor pauze (laat menu en muziekknop werken)
            for event in pygame.event.get():
                if event.type == pygame.QUIT: # gebruiker sluit het spel
                    remove_highscore_file()
                    pygame.quit()
                    sys.exit()
                # Sta muiskliks toe tijdens pauze voor menu/music
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if music_button_rect.collidepoint(event.pos):
                        if music_on:
                            if audio_available:
                                pygame.mixer.music.pause()
                            music_on = False
                        else:
                            if audio_available:
                                pygame.mixer.music.unpause()
                            music_on = True
                    if menu_button_rect.collidepoint(event.pos):
                        if audio_available:
                            pygame.mixer.music.stop()
                        return 'menu'
                elif event.type == pygame.KEYDOWN:
                    # escape wordt gebruikt om pauze op te heffen
                    if event.key == pygame.K_ESCAPE:
                        paused = False
                        # corrigeer de timer zodat de tijd tijdens pauze niet meetelt
                        if player.alive_start is not None and pause_start_time is not None:
                            pause_duration = time.time() - pause_start_time
                            player.alive_start += pause_duration
            continue

        if enemies == list() and cangonextwave == True :
            cangonextwave = False

        held = pygame.key.get_pressed()
        if held[pygame.K_RIGHT] or held[pygame.K_d]: player_dx = player.speed
        if held[pygame.K_LEFT] or held[pygame.K_q] or held[pygame.K_a]: player_dx = -player.speed
        if held[pygame.K_DOWN] or held[pygame.K_s]: player_dy = player.speed
        if held[pygame.K_UP] or held[pygame.K_z] or held[pygame.K_w]: player_dy = -player.speed



        if enemies == list():
            print("NEW WAVE STARTING")
            # toon overlay van de nieuwe wave
            next_wave_number = currentwave + 1
            await show_wave_overlay(next_wave_number)

            currentwave += 1
            enemies = await startnewave_async(currentwave, hearts)
            if currentwave == 2:
                player.add_weapon("pen")
            elif currentwave == 3:
                player.add_weapon("pine")
            elif currentwave == 4:
                player.add_weapon("PPAP")

            kills_this_wave = 0
            total_enemies_in_wave = sum(allenemywaves.get(currentwave, [0,0,0,0,0]))
  
        if player.get_hp() > 0:
            if player.has_weapon("pen"):
                if pen_time <= 0:
                    pen_time = 60
                    near = player.get_nearest_enemy(enemies)
                    # geen error bij None want leest van links naar rechts
                    if not near is None and distanceSquared(near.world_x - player.world_x, near.world_y - player.world_y) < 700**2:
                        projectiles.append(Projectile(player,near))
                        print("added pen")
                else:
                    pen_time -= 1
            if player.has_weapon("pine"):
                if pine_time <= 0:
                    pine_time = 173
                    near = player.get_nearest_enemy(enemies)
                    # geen error bij None want leest van links naar rechts
                    if not near is None and distanceSquared(near.world_x - player.world_x, near.world_y - player.world_y) < 700**2:
                        projectiles.append(Pineapple(player,near))
                        print("added pine")
                else:
                    pine_time -= 1
                


        if isinstance(invincible, int):
            invincible -= 1
            if invincible <= 0:
                invincible = False
        clock.tick(60)
        pygame.event.pump()
        for i in range(len(projectiles)-1,-1,-1):
            if not projectiles[i].handle():
                projectiles.pop(i)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                remove_highscore_file() 
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_button_rect.collidepoint(event.pos):
                    if music_on:
                        if audio_available:
                            pygame.mixer.music.pause()
                        music_on = False
                    else:
                        if audio_available:
                            pygame.mixer.music.unpause()
                        music_on = True
                if menu_button_rect.collidepoint(event.pos):
                    if audio_available:
                        pygame.mixer.music.stop()
                    return
                if main_menu_button_rect().collidepoint(event.pos):
                    if audio_available:
                        pygame.mixer.music.stop()
                    return 'menu'
                if restart_button_rect().collidepoint(event.pos):
                    return 'restart'
                if continue_button_rect().collidepoint(event.pos):
                    if player.get_hp() > 0:
                        print("CONTINUE ON ")
                        enemies = list()
                        currentwave = 6
                        cangonextwave = True
                        text = None
            elif event.type == pygame.KEYDOWN:
                
                if event.key == pygame.K_ESCAPE:
                    paused = not paused

                    if paused:
                        pause_start_time = time.time()
                    else:
                    # Corrigeer timer zodat pauze niet meetelt
                        if player.alive_start is not None:
                            pause_duration = time.time() - pause_start_time
                            player.alive_start += pause_duration

                if player.get_hp() > 0:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.look_right()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q or event.key == pygame.K_a:
                        player.look_left()
                    if event.key == pygame.K_SPACE or event.key == pygame.K_LSHIFT:
                        if stunned == False:
                            invincible = player.punch(invincible)
                        text = False
                        game_start = True
                        # start alive timer on first space press
                        if player.alive_start is None:
                            player.alive_start = time.time()
                        if enemies == list():
                            cangonextwave = True

        if not stunned and player.get_hp() > 0:
            held = pygame.key.get_pressed()
            player.is_moving = False
            if (held[pygame.K_UP] and held[pygame.K_RIGHT]) or (held[pygame.K_UP] and held[pygame.K_LEFT]) or (held[pygame.K_DOWN] and held[pygame.K_RIGHT]) or (held[pygame.K_DOWN] and held[pygame.K_LEFT]) \
               or (held[pygame.K_z] and held[pygame.K_d]) or (held[pygame.K_z] and held[pygame.K_q]) or (held[pygame.K_s] and held[pygame.K_d]) or (held[pygame.K_s] and held[pygame.K_q]) \
               or (held[pygame.K_w] and held[pygame.K_d]) or (held[pygame.K_w] and held[pygame.K_a]) or (held[pygame.K_s] and held[pygame.K_a]) or (held[pygame.K_s] and held[pygame.K_d]):
                player.speed = player.base_speed / (2**(1/2))
            else:
                player.speed = player.base_speed
            if held[pygame.K_UP] or held[pygame.K_z] or held[pygame.K_w]:
                player.up()
            if held[pygame.K_DOWN] or held[pygame.K_s]:
                player.down()
            if held[pygame.K_LEFT] or held[pygame.K_q] or held[pygame.K_a]:
                player.left()
            if held[pygame.K_RIGHT] or held[pygame.K_d]:
                player.right()

            if held[pygame.K_UP] or held[pygame.K_z] or held[pygame.K_w]:
                player.up()
                player.is_moving = True
            if held[pygame.K_DOWN] or held[pygame.K_s]:
                player.down()
                player.is_moving = True
            if held[pygame.K_LEFT] or held[pygame.K_q] or held[pygame.K_a]:
                player.left()
                player.is_moving = True
            if held[pygame.K_RIGHT] or held[pygame.K_d]:
                player.right()
                player.is_moving = True

            player.update_image()

        else:
            stunned -= 1
            if stunned <= 0:
                stunned = False

        if game_start:
            for enemy in enemies:
                enemy.trace(player)

        # Check collisions
        player_rect = player.get_world_rect()
        for heart in hearts[:]:
            if player_rect.colliderect(heart.get_rect()):
                player.regen_hp(heart.amount)
                regen_sound.play()
                hearts.remove(heart)
        for npc in enemies:
            if not npc.inv == False:
                npc.inv -= 1
                if npc.inv <= 0:
                    npc.inv = False
            npc_rect = npc.get_rect()
            for projectile in projectiles:
                if projectile.isPen and not projectile.hasCollided:
                    if projectile.get_rect().colliderect(npc_rect):
                        npc.takedamage(60)    # pen damage
                        projectile.hasCollided = True
                        dmg_sound.play()
                #   voeg ananas toe met splash dmg
                elif projectile.isPineapple and not projectile.hasCollided:
                    if projectile.get_rect().colliderect(npc_rect):
                        npc.takedamage(50)
                        projectile.hasCollided = True
                        dmg_sound.play()
                        for shrap in projectile.explode():
                            projectiles.append(shrap)
                elif projectile.isShrapnel:
                    if projectile.get_rect().colliderect(npc_rect):
                        npc.takedamage(20)
                        tick_sound.play()
                if npc.health <= 0:
                        if npc in enemies: 
                            enemies.remove(npc)
                            kills_this_wave = min(kills_this_wave + 1, total_enemies_in_wave)
                    
            if player.punching or not invincible:
                if (player_rect.colliderect(npc_rect) or player.get_rect_sword().colliderect(npc_rect)) and player.get_hp() > 0:

                    if player.punching:
                        if not npc.inv:
                            if not player.has_weapon("PPAP"):
                                npc.takedamage(50)  # punch damage
                            else:
                                npc.takedamage(100)  # ppap damages

                            npc.inv = 30
                            dmg_sound.play()
                    else:
                        if not npc.inv:
                            player.take_damage(npc.id)
                            invincible = 60
                            stunned = 10
                            dmg_sound.play()
                    
                    if npc.health <= 0:
                        if npc in enemies: 
                            enemies.remove(npc)
                            kills_this_wave = min(kills_this_wave + 1, total_enemies_in_wave)  # max 100%


                    flash_timer = flash_duration

                    if player.get_hp() <= 0 and foo:
                        text = end_game()
                        if audio_available:
                            pygame.mixer.music.stop()
                        game_over.play()
                        foo = not foo
            
                        text.y = screen_size[1] // 3
                    break
            
        
        if player.punching:
            player.punch_timer -= 1
            if player.punch_timer <= 0:
                if player.direction == "right":
                    player.image = player.sprites["right"]
                else:
                    player.image = player.sprites["left"]
                player.punching = False

        renderFrame(screen, player, enemies, hearts, punchitbox, projectiles, text)
        draw_health(screen, player)
        draw_wave_progress(screen, kills_this_wave, total_enemies_in_wave) 
        draw_timer(screen, player, currentwave)
        draw_minimap(screen, player, enemies, hearts)
        draw_highscore_left(screen, highscore) # toon highscore
        draw_boss_hp(screen, enemies)


        if player.get_hp() <= 0 or currentwave == 5:
            if currentwave == 5 and player.get_hp() > 0:
                btn2 = continue_button_rect()
                txt2 = font.render("CONTINUE", True, (0,0,0))
                pygame.draw.rect(screen, (200, 200, 200), btn2, border_radius=8)
                screen.blit(txt2, txt2.get_rect(center=btn2.center))

            btn = restart_button_rect()

            pygame.draw.rect(screen, (200, 200, 200), btn, border_radius=8)

            txt = font.render("RESTART", True, (0,0,0))
            screen.blit(txt, txt.get_rect(center=btn.center))
            # MAIN MENU button under restart
            main_btn = main_menu_button_rect()
            pygame.draw.rect(screen, (180, 180, 180), main_btn, border_radius=8)
            main_txt = font.render("MAIN MENU", True, (0,0,0))
            screen.blit(main_txt, main_txt.get_rect(center=main_btn.center))

        if flash_timer > 0 and stunned:
            overlay = pygame.Surface(screen_size)
            overlay.set_alpha(100)
            overlay.fill((255,0,0))
            screen.blit(overlay, (0,0))
            flash_timer -= 1

        # draw menu button (with hover) and music button
        mpos = pygame.mouse.get_pos()
        hover = menu_button_rect.collidepoint(mpos)
        draw_menu_button(screen, menu_button_rect, hover=hover)

        btn_color = (100, 220, 100) if music_on else (220, 100, 100)  # groen = audio aan, rood = audio uit
        pygame.draw.rect(screen, btn_color, music_button_rect, border_radius=6)

        screen.blit(mute_img, (music_button_rect.x, music_button_rect.y))

        snow_surface.fill((0, 0, 0, 0)) # transparante laag waarover ik de sneeuw wil plaatsen
        for snow in snowflakes: # loop door alle sneeuw
            snow.update(player_dx, player_dy) # parallax-effect wanneer speler beweegt
            snow.draw(snow_surface, MINIMAP_RECT)

        screen.blit(snow_surface, (0, 0)) # teken sneeuw op transparante sneeuwlaag

        flip()
        await asyncio.sleep(0)

async def run_app():
    while True:
        start = await main_menu()
        if not start:
            break
        # Enter game loop; `main()` may return control flags:
        #  - 'restart' : restart game immediately
        #  - 'menu'    : return to main menu
        #  - None/other: exit to menu
        while True:
            result = await main()
            if result == 'restart':
                # restart the game without showing main menu
                continue
            if result == 'menu':
                # go back to main menu
                break
            # any other result -> go back to main menu
            break

if __name__ == "__main__":
    try:
        asyncio.run(run_app())
    finally:
        pygame.quit()