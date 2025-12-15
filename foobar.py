import pygame
from pygame.display import flip
def main():
    pygame.init()

    screen_size = (1024, 768)

    def create_main_surface(size):
        return pygame.display.set_mode(size)

    screen = create_main_surface(screen_size)
    pygame.display.set_caption("Circle")

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((0, 0, 0)) 

        # draw circle
        pygame.draw.circle(
            screen,
            (0, 255, 0),          # green
            (512, 384),           # center of screen
            50                    # radius
        )

        flip()
    pygame.quit()


if __name__ == "__main__":
    main()
