import pygame
import time
from pygame.display import flip
from random import randint

MINIMAP_SIZE = (200, 150)  # breedte, hoogte van de minimap
MINIMAP_PADDING = 20        # afstand van schermrand
MINIMAP_BG_COLOR = (50, 50, 50)
MINIMAP_PLAYER_COLOR = (255, 0, 0)
MINIMAP_BORDER_COLOR = (200, 200, 200)

screen_size = (1024, 768)

pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Fixed Game")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arialblack", 24)

background_image = pygame.image.load("background/background-map 4 (desert).png").convert()
background_width, background_height = background_image.get_size()
scroll_x, scroll_y = 0, 0

allenemywaves = {1: [2,3,3],2: [1,2,1],3: [0,0,0],4: [0,0,0]}
enemies = []
punchitbox = None


class Player:
    def __init__(self):
        self.__maxHp = 10
        self.__health = self.__maxHp
        self.base_speed = 3
        self.speed = self.base_speed
        self.width = 60
        self.height = 100
        # Player is always at the center of the screen
        self.screen_x = screen_size[0] // 2 - self.width // 2
        self.screen_y = screen_size[1] // 2 - self.height // 2
        # World position tracks where the player is in the game world
        self.world_x = background_width // 2 - self.width //2
        self.world_y = background_height // 2 - self.height // 2

        global scroll_x, scroll_y
        scroll_x = max(0, min(self.world_x - screen_size[0] // 2, background_width - screen_size[0]))
        scroll_y = max(0, min(self.world_y - screen_size[1] // 2, background_height - screen_size[1]))


        self.direction = "right"
        self.is_moving = False
        self.walk_frame = 0
        self.walk_timer = 0

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

        self.image = self.sprites["right"]
        self.punching = False
        self.punch_timer = 0

    def draw(self, screen):
        self.draw_shadow(screen)
        # Always draw player at the center of the screen
        screen.blit(self.image, (self.screen_x, self.screen_y))


    def draw_shadow(self, screen):
        shadow_width = self.width * 0.8
        shadow_height = self.height * 0.25
        shadow_x = self.screen_x + (self.width - shadow_width) / 2
        shadow_y = self.screen_y + self.height - shadow_height * 0.6


        shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 100), shadow.get_rect())  # 100 = alpha
        screen.blit(shadow, (shadow_x, shadow_y))

    def get_hp(self):
        return self.__health

    def take_damage(self, dmg: int):
        self.__health -= dmg
    
    def regen_hp(self, regen):
        self.__health += regen
        if self.__health > self.__maxHp:
            self.__health = self.__maxHp

    def punch(self):
        if not self.punching:
            print("punch")
            if self.direction == "right":
                self.image = self.sprites["right_punch"]
            else:
                self.image = self.sprites["left_punch"]
            self.punching = True
            self.punch_timer = 30   # buffer frames
            punchitbox = hitBox(0.5,[40,40],self)
            global punch_sound
            punch_sound.play()
            for npc in enemies:
                if punchitbox.get_rect().colliderect(npc.get_rect()):
                    npc.takedamage(2)
                    print("smacked an enemy ")


    def up(self):
        global scroll_y
        self.world_y -= self.speed
        self.world_y = max(0, min(self.world_y, background_height - self.height))
        scroll_y = max(0, min(self.world_y - screen_size[1] // 2, background_height - screen_size[1]))

    def down(self):
        global scroll_y
        self.world_y += self.speed
        self.world_y = max(0, min(self.world_y, background_height - self.height))
        scroll_y = max(0, min(self.world_y - screen_size[1] // 2, background_height - screen_size[1]))

    def left(self):
        global scroll_x
        self.world_x -= self.speed
        self.world_x = max(0, min(self.world_x, background_width - self.width))
        scroll_x = max(0, min(self.world_x - screen_size[0] // 2, background_width - screen_size[0]))

    def right(self):
        global scroll_x
        self.world_x += self.speed
        self.world_x = max(0, min(self.world_x, background_width - self.width))
        scroll_x = max(0, min(self.world_x - screen_size[0] // 2, background_width - screen_size[0]))

    def look_left(self):
        self.direction = "left"

    def look_right(self):
        self.direction = "right"

    def update_image(self):
        if self.punching:
            self.image = self.sprites[f"{self.direction}_punch"]
        else:
            if self.is_moving:
                # Wissel tussen standaard en walking sprite
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

    def get_rect(self):
        return pygame.Rect(self.screen_x, self.screen_y, self.width, self.height)
    
    def get_world_rect(self):
        # Return collision box based on world position
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
    
    def draw(self, screen):
        rect = self.get_rect()
        screen_rect = pygame.Rect(
            rect.x - scroll_x,
            rect.y - scroll_y,
            rect.width,
            rect.height
        )

class Npc:
    def __init__(self):
        self.world_x, self.world_y = randint(0, background_width), randint(0, background_height)
        self.width, self.height = 45, 60
        self.base_speed = 3
        self.speed = self.base_speed
        self.shrink_width = 22.5
        self.shrink_height = 45
        self.health = 1
    def draw_shadow(self, screen):
        shadow_width = self.width * 0.8
        shadow_height = self.height * 0.25
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        shadow_x = screen_x + (self.width - shadow_width) / 2
        shadow_y = screen_y + self.height - shadow_height * 0.6  # pas hier eventueel offset aan
        shadow = pygame.Surface((shadow_width, shadow_height), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0,0,0,100), shadow.get_rect())
        screen.blit(shadow, (shadow_x, shadow_y))
        self.health = 10
    
    def trace(self, player: Player):
        m = getDir((self.world_x, self.world_y), (player.world_x, player.world_y))
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
        if self.health - amount <= 0 : 
            self.health = 0
        else:
            self.health -= amount

def getDir(selfCoords: tuple, playerCoords: tuple):
    dx, dy = playerCoords[0] - selfCoords[0], playerCoords[1] - selfCoords[1]
    size = (dx**2 + dy**2)**(1/2)
    return (dx/size, dy/size)

class Labubu(Npc):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/Labubu - sprite/Labubu - gold.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.health = 8

    def draw(self, screen):
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        screen.blit(self.image, (screen_x, screen_y))

    def get_rect(self):
        shrink_w, shrink_h = 30, 40
        return pygame.Rect(
            self.world_x + shrink_w // 2,
            self.world_y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )


class Zombie(Npc):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/Zombie - sprite/zombie.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.health = 3

    def draw(self, screen):
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        screen.blit(self.image, (screen_x, screen_y))
    def get_rect(self):
        shrink_w, shrink_h = 30, 40
        return pygame.Rect(
            self.world_x + shrink_w // 2,
            self.world_y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )

class Fruit(Npc):
    def __init__(self):
        super().__init__()
        self.health = 5

    def draw(self, screen):
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        pygame.draw.rect(
            screen,
            (0, 0, 200),
            (screen_x, screen_y, self.width, self.height)
        )

    def get_rect(self):
        shrink_w, shrink_h = 5, 10
        return pygame.Rect(
            self.world_x + shrink_w // 2,
            self.world_y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )


class Boss(Npc):
    def __init__(self):
        super().__init__()
        self.width = 150
        self.height = 200
        self.world_x = background_width // 2 - self.width
        self.world_y = background_height // 8
        self.image = pygame.image.load("sprites/Labubu - sprite/Labubu - blue.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.health = 50

    def get_rect(self):
        shrink_w, shrink_h = 80, 120
        return pygame.Rect(
            self.world_x + shrink_w // 2,
            self.world_y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )
    
    def draw(self, screen):
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        screen.blit(self.image, (screen_x, screen_y))


class Text:
    def __init__(self, path="background/tutorial gamecontrols.png"):
        self.width = 500
        self.height = 200
        self.image = pygame.image.load(path).convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] // 2) + 50

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


def renderFrame(screen, player: Player, npcs: list, hit :hitBox , text=None):
    screen.blit(background_image, (0, 0), area=pygame.Rect(scroll_x, scroll_y, screen_size[0], screen_size[1]))
    
    drawables = npcs[:] # lijst kopie
    drawables.sort(key=lambda obj: obj.world_y + obj.height)
    
    for obj in drawables:
        if hasattr(obj, "draw_shadow"):
            obj.draw_shadow(screen)

    for obj in drawables:
        obj.draw(screen)
    
    player.draw(screen)
    if text:
        text.draw(screen)

    if hit:
        hit.draw(screen)

def draw_health(screen, player: Player):
    padding = 8

    hp_text = font.render(
        f"HP: {player.get_hp()} / 10",
        True,
        (220,30,30)
    )

    bg_rect = hp_text.get_rect(topleft=(20,20))
    bg_rect.inflate_ip(padding*2, padding*2)

    pygame.draw.rect(screen, (180,180,180), bg_rect, border_radius=6)

    text_rect = hp_text.get_rect(center=bg_rect.center)
    screen.blit(hp_text, text_rect)

def end_game():
    return Text("background/game_over.png")

def restart_button_rect():
    return pygame.Rect(
        screen_size[0] // 2 - 100,
        screen_size[1] // 2 + 100,
        200,
        50
    )

def startnewave(currentwave):
    enemies = []
    fruit,labubu,zombie = allenemywaves[currentwave]
    for _ in range(fruit):
        enemies.append(Fruit())
    for _ in range(labubu):
        enemies.append(Labubu())
    for _ in range(zombie):
        enemies.append(Zombie())
    enemies.append(Boss())
    return enemies

def draw_minimap(screen, player: Player, npcs: list):
    # positie linksonder
    x = MINIMAP_PADDING
    y = screen_size[1] - MINIMAP_SIZE[1] - MINIMAP_PADDING

    # achtergrond minimap
    minimap_rect = pygame.Rect(x, y, MINIMAP_SIZE[0], MINIMAP_SIZE[1])
    pygame.draw.rect(screen, MINIMAP_BG_COLOR, minimap_rect, border_radius=4)
    pygame.draw.rect(screen, MINIMAP_BORDER_COLOR, minimap_rect, 2, border_radius=4)

    mini_bg = pygame.transform.smoothscale(background_image, MINIMAP_SIZE)
    screen.blit(mini_bg, (x,y))

    # schaal factor
    scale_x = MINIMAP_SIZE[0] / background_width
    scale_y = MINIMAP_SIZE[1] / background_height

    for npc in npcs:
        npc_rect = npc.get_rect()
        mini_npc_x = x + int(npc.world_x * scale_x)
        mini_npc_y = y + int(npc.world_y * scale_y)
        # Kleine rechthoek of cirkel als representatie
        pygame.draw.rect(screen, (0,200,0), (mini_npc_x, mini_npc_y, 4, 4))

    # speler positie
    px = x + int(player.world_x * scale_x)
    py = y + int(player.world_y * scale_y)
    pygame.draw.circle(screen, MINIMAP_PLAYER_COLOR, (px, py), 5)

def main():
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/background.mp3')
    pygame.mixer.music.play(-1, 0, 0)
    pygame.mixer.music.set_volume(0.25)
    dmg_sound = pygame.mixer.Sound('sounds/damage.mp3')
    game_over = pygame.mixer.Sound("sounds/gameover.mp3")
    global punch_sound
    punch_sound = pygame.mixer.Sound('sounds/punch.mp3')

    foo = True
    flash_timer = 0
    flash_duration = 5
    player = Player()
    text = Text()
    invincible = False
    stunned = False
    game_start = False
    currentwave = 1
    enemies = startnewave(currentwave)
    
    minimap_update_timer = 0  
    minimap_update_interval = 120 
    minimap_surface = pygame.Surface(MINIMAP_SIZE)  

    running = True
    while running:
        if enemies == list() :
            print("NEW WAVE STARTING")
            currentwave =+ 1
            enemies = startnewave(currentwave)
        if isinstance(invincible, int):
            invincible -= 1
            if invincible <= 0:
                invincible = False
        clock.tick(60)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if player.get_hp() <= 0:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if restart_button_rect().collidepoint(event.pos):
                        main()
                        return

            elif event.type == pygame.KEYDOWN:
                if player.get_hp() > 0:
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        player.look_right()
                    if event.key == pygame.K_LEFT or event.key == pygame.K_q:
                        player.look_left()
                    if event.key == pygame.K_SPACE or event.key == pygame.K_LSHIFT:
                        if stunned == False:
                            player.punch()
                        text = False
                        game_start = True

        if not stunned and player.get_hp() > 0:
            held = pygame.key.get_pressed()
            player.is_moving = False
            if (held[pygame.K_UP] and held[pygame.K_RIGHT]) or (held[pygame.K_UP] and held[pygame.K_LEFT]) or (held[pygame.K_DOWN] and held[pygame.K_RIGHT]) or (held[pygame.K_DOWN] and held[pygame.K_LEFT]) or (held[pygame.K_z] and held[pygame.K_d]) or (held[pygame.K_z] and held[pygame.K_q]) or (held[pygame.K_s] and held[pygame.K_d]) or (held[pygame.K_s] and held[pygame.K_q]):
                player.speed = player.base_speed / (2**(1/2))
            else:
                player.speed = player.base_speed
            if held[pygame.K_UP] or held[pygame.K_z]:
                player.up()
            if held[pygame.K_DOWN] or held[pygame.K_s]:
                player.down()
            if held[pygame.K_LEFT] or held[pygame.K_q]:
                player.left()
            if held[pygame.K_RIGHT] or held[pygame.K_d]:
                player.right()

            if held[pygame.K_UP] or held[pygame.K_z]:
                player.up()
                player.is_moving = True
            if held[pygame.K_DOWN] or held[pygame.K_s]:
                player.down()
                player.is_moving = True
            if held[pygame.K_LEFT] or held[pygame.K_q]:
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
        if invincible == False:
            for npc in enemies:
                if npc.health <= 0 :
                    enemies.remove(npc)
                if player_rect.colliderect(npc.get_rect()) and player.get_hp() > 0:
                    invincible = 60        # 2 sec iframes
                    stunned = 10
                    player.take_damage(2)
                    npc.takedamage(10)
                    dmg_sound.play()

                    flash_timer = flash_duration

                    print(player.get_hp())
                    if player.get_hp() <= 0 and foo:
                        text = end_game()
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

        renderFrame(screen, player, enemies,punchitbox, text)
        draw_health(screen, player)
        if minimap_update_timer <= 0:
            minimap_surface.fill(MINIMAP_BG_COLOR)
            mini_bg = pygame.transform.smoothscale(background_image, MINIMAP_SIZE)
            minimap_surface.blit(mini_bg, (0,0))

            # NPC posities
            scale_x = MINIMAP_SIZE[0] / background_width
            scale_y = MINIMAP_SIZE[1] / background_height
            for npc in enemies:
                mini_npc_x = int(npc.world_x * scale_x)
                mini_npc_y = int(npc.world_y * scale_y)
                pygame.draw.rect(minimap_surface, (0,200,0), (mini_npc_x, mini_npc_y, 4, 4))
    
            minimap_update_timer = minimap_update_interval
        else:
            minimap_update_timer -= 1

        screen.blit(minimap_surface, (MINIMAP_PADDING, screen_size[1] - MINIMAP_SIZE[1] - MINIMAP_PADDING))

        px = MINIMAP_PADDING + int(player.world_x * scale_x)
        py = screen_size[1] - MINIMAP_SIZE[1] - MINIMAP_PADDING + int(player.world_y * scale_y)
        pygame.draw.circle(screen, MINIMAP_PLAYER_COLOR, (px, py), 5)

        if player.get_hp() <= 0:
            btn = restart_button_rect()
            pygame.draw.rect(screen, (200, 200, 200), btn, border_radius=8)

            txt = font.render("RESTART", True, (0,0,0))
            screen.blit(txt, txt.get_rect(center=btn.center))

        if flash_timer > 0:
            overlay = pygame.Surface(screen_size)
            overlay.set_alpha(100)
            overlay.fill((255,0,0))
            screen.blit(overlay, (0,0))
            flash_timer -= 1
            
        flip()

    pygame.quit()

if __name__ == "__main__":
    main()