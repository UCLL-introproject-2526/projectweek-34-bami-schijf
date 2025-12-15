import pygame
from pygame.display import flip

screen_size = (1024, 768)

class State:
    def __init__(self):
        self.x = 100
        self.y = 0
    
    def up(self):
        if self.y > 0:
            self.y -= 1
            if self.y < 0:
                self.y = 0
    def down(self):
        if self.y < screen_size[1]:
            self.y += 1
            if self.y > screen_size[1]:
                self.y = screen_size[1]
    def left(self):
        if self.x > 0:
            self.x -= 1 
            if self.x < 0:
                self.x = 0
    def right(self):
        if self.x < screen_size[0]:
            self.x += 1
            if self.x > screen_size[0]:
                self.x = screen_size[0]

def main():
    pygame.init()
    

    circle = State()

    def create_main_surface(size):
        return pygame.display.set_mode(size)
    def renderFrame():
        screen.fill((0, 0, 0))

        # draw circle
        pygame.draw.circle(
            screen,
            (0, 255, 0),          # green
            (circle.x, circle.y),           # center of screen
            50                    # radius
        )
        flip()
        

    screen = create_main_surface(screen_size)
    pygame.display.set_caption("Circle")

    running = True

    while running:
        pygame.event.pump()
        heldKeys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                ...
        if heldKeys[pygame.K_UP]:
            circle.up()
        if heldKeys[pygame.K_DOWN]:
            circle.down()
        if heldKeys[pygame.K_RIGHT]:
            circle.right()
        if heldKeys[pygame.K_LEFT]:
            circle.left()

        renderFrame()
    pygame.quit()


if __name__ == "__main__":
    main()
