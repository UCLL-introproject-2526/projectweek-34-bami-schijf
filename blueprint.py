import pygame
from pygame.display import flip
from random import randint

screen_size = (1024, 768)

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
        self.image = pygame.image.load("sprites/PPAP - sprite/PPAP - right.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def up(self):
        self.y = max(0, self.y - self.speed)

    def down(self):
        self.y = min(screen_size[1] - self.height, self.y + self.speed)

    def left(self):
        self.x = max(0, self.x - self.speed)

    def right(self):
        self.x = min(screen_size[0] - self.width, self.x + self.speed)

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))
    
    def look_left(self):
        self.image = pygame.image.load("sprites/PPAP - sprite/PPAP - left.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

    def look_right(self):
        self.image = pygame.image.load("sprites/PPAP - sprite/PPAP - right.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))




class Npc:
    def __init__(self):
        self.x, self.y = randint(0, screen_size[0]), randint(0,screen_size[1])
        self.width, self.height = 45, 60
        self.speed = 3
    def trace(self, player: Player):
        m = getDir((self.x, self.y), (player.x, player.y))
        self.x += m[0] * self.speed
        self.y += m[1] * self.speed

    
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

class Fruit(Npc):
    def draw(self, screen):
        pygame.draw.rect(
            screen,
            (0, 0, 200),
            (self.x, self.y, self.width, self.height)
        )


class Boss(Npc):
    def __init__(self):
        super().__init__()
        self.x = screen_size[0] // 2 - self.width
        self.y = screen_size[1] // 8
        self.width = 150
        self.height = 200
        self.image = pygame.image.load("sprites/Labubu - sprite/Labubu - blue.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (self.width, self.height))
        self.speed = 1

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

        


def renderFrame(screen, player: Player, npcs: list):
    screen.fill((0, 0, 0))
    player.draw(screen)
    for npc in npcs:
        npc.draw(screen)
    flip()

def main():

    player = Player()
    running = True
    enemies = []
    for _ in range(3):
        enemies.append(Fruit())
    for _ in range(2):
        enemies.append(Labubu())
    for _ in range(4):
        enemies.append(Zombie())

    enemies.append(Boss())

    while running:
        clock.tick(60)
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    player.look_right()
                    print("look right")
                elif event.key == pygame.K_LEFT:
                    player.look_left()
                    print("look left")

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
            enemy.trace(player)
        renderFrame(screen, player, enemies)

    pygame.quit()

if __name__ == "__main__":
    main()
