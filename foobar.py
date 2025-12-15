import pygame
from pygame.display import flip
def main():
    pygame.init()

    screen_size = (1024, 768)

    def create_main_surface(size):
        return pygame.display.set_mode(size)
    def renderFrame():

        # draw circle
        pygame.draw.circle(
            screen,
            (0, 255, 0),          # green
            (512, 384),           # center of screen
            50                    # radius
        )
        flip()
        

    screen = create_main_surface(screen_size)
    pygame.display.set_caption("Circle")

    running = True

    while running:
        pygame.event.pump()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        renderFrame()
    pygame.quit()


if __name__ == "__main__":
    main()
