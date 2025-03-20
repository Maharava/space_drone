import pygame
from game_config import *

class Camera:
    def __init__(self, width, height):
        self.rect = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
    
    def update(self, target):
        # Keep target centered
        x = -target.rect.centerx + SCREEN_WIDTH // 2
        y = -target.rect.centery + SCREEN_HEIGHT // 2
        
        # Limit scrolling to world boundaries
        x = min(0, x)  # Left edge
        y = min(0, y)  # Top edge
        x = max(-(WORLD_WIDTH - SCREEN_WIDTH), x)  # Right edge
        y = max(-(WORLD_HEIGHT - SCREEN_HEIGHT), y)  # Bottom edge
        
        self.rect.x = x
        self.rect.y = y
    
    def apply(self, entity):
        return entity.rect.move(self.rect.topleft)
