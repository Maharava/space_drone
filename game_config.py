import pygame

# Screen setup
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# World size (much larger than screen)
WORLD_WIDTH, WORLD_HEIGHT = 3200, 2400

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GREY = (100, 100, 100)
SILVER = (192, 192, 192)
BROWN = (139, 69, 19)
PURPLE = (128, 0, 128)
DARK_GREY = (50, 50, 50)

# Clock for FPS
clock = pygame.time.Clock()
FPS = 60

# Inventory grid config
INVENTORY_COLS = 5
INVENTORY_ROWS = 4
MAX_STACK_SIZE = 20
