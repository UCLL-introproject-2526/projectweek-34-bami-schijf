import pygame


# Initialize Pygame
pygame.init()

screen_size = (1024, 768)

def create_main_window(size):
    while True:
        pygame.display.set_mode(size)

create_main_window(screen_size)