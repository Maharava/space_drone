import pygame
import random
import math
from game_config import *

class Asteroid(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Try to load image or use circle
        self.size = random.randint(20, 50)
        try:
            self.image = pygame.image.load("assets/asteroid.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except:
            # Create circle if image not found
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, GREY, (self.size // 2, self.size // 2), self.size // 2)
        
        # Random position anywhere in the world
        x = random.randint(50, WORLD_WIDTH - 50)
        y = random.randint(50, WORLD_HEIGHT - 50)
                
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(self.rect.center)
        self.health = self.size // 5
        
        # Random very slow movement
        angle = random.uniform(0, math.pi * 2)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = random.uniform(0.1, 0.3)  # Greatly reduced speed
    
    def update(self, game_state):
        # Skip updates if inventory is open
        if game_state != 0:  # GAME_RUNNING = 0
            return
            
        self.position += self.velocity * self.speed
        
        # Wrap around world boundaries
        if self.position.x < 0:
            self.position.x = WORLD_WIDTH
        elif self.position.x > WORLD_WIDTH:
            self.position.x = 0
            
        if self.position.y < 0:
            self.position.y = WORLD_HEIGHT
        elif self.position.y > WORLD_HEIGHT:
            self.position.y = 0
        
        self.rect.center = self.position
    
    def damage(self, amount=1):
        self.health -= amount
        return self.health <= 0
    
    def get_ore_drops(self):
        """Returns a list of ores dropped by this asteroid"""
        # Size determines how many ore pieces drop
        drops = []
        
        # Base number of drops based on size
        drop_count = max(1, self.size // 10)
        
        # Add random variation
        drop_count += random.randint(-1, 2)
        drop_count = max(1, drop_count)  # Minimum 1 drop
        
        for _ in range(drop_count):
            # Random ore with weightings
            roll = random.random()
            if roll < 0.5:
                drops.append("low-grade")  # Most common
            elif roll < 0.8:
                drops.append("high-grade")
            elif roll < 0.95:
                drops.append("rare-ore")
            else:
                drops.append("silver")  # Least common
        
        return drops
