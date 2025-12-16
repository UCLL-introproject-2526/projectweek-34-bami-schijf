import pygame
import time
from pygame.display import flip
from random import randint

screen_size = (1024, 768)
Weapon = "Fist"

pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Fixed Game")
clock = pygame.time.Clock()


pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Fixed Game")
clock = pygame.time.Clock()


class Player:
    def __init__(self):
        self.speed = 5
        self.x = screen_size[0] // 2
        self.y = screen_size[1] // 2
        self.width = 60
        self.height = 100
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
        screen.blit(self.image, (self.x, self.y))

    def look_left(self):
        self.direction = "left"
        if not self.punching:
            self.image = self.sprites["left"]

    def look_right(self):
        self.direction = "right"
        if not self.punching:
            self.image = self.sprites["right"]

    def punch(self):
        if self.direction == "right":
            self.image = self.sprites["right_punch"]
        else:
            self.image = self.sprites["left_punch"]
        self.punching = True
        self.punch_timer = 10   # aantal frames zichtbaar

    def up(self):
        self.y = max(0, self.y - self.speed)

    def down(self):
        self.y = min(screen_size[1] - self.height, self.y + self.speed)

    def left(self):
        self.x = max(0, self.x - self.speed)

    def right(self):
        self.x = min(screen_size[0] - self.width, self.x + self.speed)

<<<<<<< HEAD
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def look_left(self):
        self.image = pygame.image.load("sprites/PPAP - sprite/PPAP - left.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def look_right(self):
        self.image = pygame.image.load("sprites/PPAP - sprite/PPAP - right.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def get_rect(self): #COLLISION BOX PLAYER
=======
    def get_rect(self):
>>>>>>> 4c681bdd3270ac3da835ae9ed9c7d43ccb364a8e
        return pygame.Rect(self.x, self.y, self.width, self.height)

class hitBox:
    def __init__(self,duration,size,player: Player):
        self.startTime = time.time()
        self.duration = duration
        self.active = True
        self.player = player
        self.size = size
        


    def update(self, dt):
            pygame.draw.rect(
            screen,
            (0, 200, 0),
            (self.player.x, self.player.y, self.size[0], self.size[1]),
            100
        )
            self.time_left -= dt
            if self.time_left <= 0:
                self.active = False
                self.player.look_right()



class Npc:
    def __init__(self):
        self.x, self.y = randint(0, screen_size[0]), randint(0, screen_size[1])
        self.width, self.height = 45, 60
        self.speed = 3
         #CREATE COLLISION BOX NPC
        self.shrink_width = 22.5
        self.shrink_height = 45
        
    def trace(self, player: Player):
        m = getDir((self.x, self.y), (player.x, player.y))
        self.x += m[0] * self.speed
        self.y += m[1] * self.speed

    def get_rect(self): #RETURN COLLISION BOX NPC
        return pygame.Rect(
            self.x + self.shrink_width // 2,
            self.y + self.shrink_height // 2,
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
        self.speed = 4
 
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

    def get_rect(self):
        shrink_w, shrink_h = 30, 40
        return pygame.Rect(
            self.x + shrink_w // 2,
            self.y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )


class Zombie(Npc):
    def __init__(self):
        super().__init__()
        self.speed = 2
    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (0, 200, 0),
            (self.x, self.y, self.width, self.height)
        )

    def get_rect(self):
        shrink_w, shrink_h = 30, 40
        return pygame.Rect(
            self.x + shrink_w // 2,
            self.y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )


class Fruit(Npc):
    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (0, 0, 200),
            (self.x, self.y, self.width, self.height)
        )

    def get_rect(self):
        shrink_w, shrink_h = 5, 10
    def get_rect(self): #COLLISION BOX FRUIT
        shrink_w, shrink_h = 30, 40
        return pygame.Rect(
            self.x + shrink_w // 2,
            self.y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )


class Boss(Npc):
    def __init__(self):
        super().__init__()
        self.width = 150
        self.height = 200
        self.x = screen_size[0] // 2 - self.width
        self.y = screen_size[1] // 8
        self.image = pygame.image.load("sprites/Labubu - sprite/Labubu - blue.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.speed = 1

    def get_rect(self):
        shrink_w, shrink_h = 80, 120
        return pygame.Rect(
            self.x + shrink_w // 2,
            self.y + shrink_h // 2,
            self.width - shrink_w,
            self.height - shrink_h
        )
    
    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class TutorialText:
    def __init__(self):
        self.width = 500
        self.height = 200
        self.image = pygame.image.load("background/tutorial gamecontrols.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.x = (screen_size[0] - self.width) // 2
        self.y = (screen_size[1] // 2) + 50

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


def renderFrame(screen, player: Player, npcs: list, tutorial=None):
    screen.fill((0, 0, 0))
    if tutorial:
        tutorial.draw(screen)
    drawables = npcs + [player]
    drawables.sort(key=lambda obj: obj.y + obj.height)
    for obj in drawables:
        obj.draw(screen)


def main():
<<<<<<< HEAD
    pygame.init()
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("Fixed Game")
    clock = pygame.time.Clock()
    pygame.mixer.init()
    pygame.mixer.music.load('sound/background.mp3') #background music
    pygame.mixer.music.play(-1, 0.0) #music loop
=======
>>>>>>> 4c681bdd3270ac3da835ae9ed9c7d43ccb364a8e

    player = Player()
    tutorial = TutorialText()

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
        clock.tick(60)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.look_right()
                elif event.key == pygame.K_LEFT:
                    player.look_left()
                elif event.key == pygame.K_SPACE:
                    player.punch()
                    print(player)
                    newhitbox = hitBox(0.5,(20,20),player)

        old_x, old_y = player.x, player.y

        held = pygame.key.get_pressed()
        if held[pygame.K_UP]:
            player.up()
        if held[pygame.K_DOWN]:
            player.down()
        if held[pygame.K_LEFT]:
            player.left()
        if held[pygame.K_RIGHT]:
            player.right()
        for enemy in enemies:
            ...
            # enemy.trace(player)

        player_rect = player.get_rect()
        for npc in enemies:
            if player_rect.colliderect(npc.get_rect()):
                player.x, player.y = old_x, old_y
                break
    
        if player.punching:
            player.punch_timer -= 1
            if player.punch_timer <= 0:
                if player.direction == "right":
                    player.image = player.sprites["right"]
                else:
                    player.image = player.sprites["left"]
                player.punching = False


        renderFrame(screen, player, enemies)

    pygame.quit()


if __name__ == "__main__":
    main()
