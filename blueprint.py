import pygame
import time
from pygame.display import flip
from random import randint

screen_size = (1024, 768)

pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Fixed Game")
clock = pygame.time.Clock()

background_image = pygame.image.load("background/background-map 4 (desert).png").convert()
background_width, background_height = background_image.get_size()
scroll_x, scroll_y = 0, 0


class Player:
    def __init__(self):
        self.__maxHp = 10
        self.__health = self.__maxHp
        self.base_speed = 6
        self.speed = self.base_speed
        self.width = 60
        self.height = 100
        # Player is always at the center of the screen
        self.screen_x = screen_size[0] // 2 - self.width // 2
        self.screen_y = screen_size[1] // 2 - self.height // 2
        # World position tracks where the player is in the game world
        self.world_x = screen_size[0] // 2
        self.world_y = screen_size[1] // 2
        self.direction = "right"

        self.sprites = {
            "left": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - left.png").convert_alpha(),
                (self.width, self.height)
            ),
            "right": pygame.transform.scale(
                pygame.image.load("sprites/PPAP - sprite/PPAP - right.png").convert_alpha(),
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
        # Always draw player at the center of the screen
        screen.blit(self.image, (self.screen_x, self.screen_y))

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
            if self.direction == "left":
                self.image = self.sprites["left_punch"]
            else:
                self.image = self.sprites["right_punch"]
        else:
            if self.direction == "left":
                self.image = self.sprites["left"]
            else:
                self.image = self.sprites["right"]

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
        self.x = player.x
        self.y = player.y
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


class Npc:
    def __init__(self):
        self.world_x, self.world_y = randint(0, background_width), randint(0, background_height)
        self.width, self.height = 45, 60
        self.base_speed = 3
        self.speed = self.base_speed
        self.shrink_width = 22.5
        self.shrink_height = 45
        
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


def getDir(selfCoords: tuple, playerCoords: tuple):
    dx, dy = playerCoords[0] - selfCoords[0], playerCoords[1] - selfCoords[1]
    size = (dx**2 + dy**2)**(1/2)
    return (dx/size, dy/size)


class Labubu(Npc):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load("sprites/Labubu - sprite/Labubu - gold.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

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
    def draw(self, screen):
        screen_x, screen_y = self.get_screen_pos(scroll_x, scroll_y)
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (screen_x, screen_y, self.width, self.height)
        )

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


def renderFrame(screen, player: Player, npcs: list, text=None):
    screen.blit(background_image, (0, 0), area=pygame.Rect(scroll_x, scroll_y, screen_size[0], screen_size[1]))
    
    
    drawables = npcs[:] # lijst kopie
    drawables.sort(key=lambda obj: obj.world_y + obj.height)
    
    for obj in drawables:
        obj.draw(screen)
    
    player.draw(screen)
    if text:
        text.draw(screen)

def end_game():
    return Text("background/game_over.png")


def main():
    pygame.mixer.init()
    pygame.mixer.music.load('sounds/background.mp3')
    pygame.mixer.music.play(-1, 0, 0)
    dmg_sound = pygame.mixer.Sound('sounds/take_dmg.mp3')
    game_over = pygame.mixer.Sound("sounds/game_over.mp3")

    foo = True
    player = Player()
    text = Text()
    invincible = False
    stunned = False
    game_start = False
    enemies = []
    for _ in range(3):
        enemies.append(Fruit())
    for _ in range(2):
        enemies.append(Labubu())
    for _ in range(4):
        enemies.append(Zombie())
    enemies.append(Boss())
    
    running = True
    while running:
        if isinstance(invincible, int):
            invincible -= 1
            if invincible <= 0:
                invincible = False
        clock.tick(60)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
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
                if player_rect.colliderect(npc.get_rect()) and player.get_hp() > 0:
                    invincible = 60        # 2 sec iframes
                    stunned = 10
                    player.take_damage(2)
                    dmg_sound.play()

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

        renderFrame(screen, player, enemies, text)
        flip()

    pygame.quit()


if __name__ == "__main__":
    main()