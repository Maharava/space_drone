import pygame
import math
from game_config import *

class Weapon(pygame.sprite.Sprite):
    """Base class for all weapon projectiles"""
    def __init__(self, position=None, direction=None, module=None):
        super().__init__()
        self.active = False
        self.module = module
        
        if position and direction and module:
            self.initialize(position, direction, module)
    
    def get_module_stat(self, stat_name, default_value):
        """Helper to get a stat from the module"""
        if self.module and hasattr(self.module, 'stats') and stat_name in self.module.stats:
            return self.module.stats[stat_name]
        return default_value
    
    def initialize(self, position, direction, module):
        """Initialize for use from pool"""
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2(direction)
        self.module = module
        
        # Get weapon properties from module
        size = self.get_module_stat('size', (5, 5))
        color = self.get_module_stat('color', RED)
        
        # Create base sprite
        self.original_image = pygame.Surface(size)
        self.original_image.fill(color)
        
        # Calculate angle from direction vector (degrees)
        # Convert from direction vector to angle (0° is up, 90° is right)
        angle = math.degrees(math.atan2(-self.direction.x, -self.direction.y))
        
        # Rotate the image
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=position)
        self.active = True
    
    def update(self, game_state):
        """Update position and check bounds"""
        # Skip updates if inventory is open
        if game_state != 0:  # GAME_RUNNING = 0
            return
        
        speed = self.get_module_stat('speed', 10)
        self.position += self.direction * speed
        self.rect.center = self.position
        
        # Remove if off world
        if (self.position.x < 0 or self.position.x > WORLD_WIDTH or 
            self.position.y < 0 or self.position.y > WORLD_HEIGHT):
            self.active = False
            self.kill()

# Factory function to create weapons
def create_weapon(module, position, direction):
    """Create a weapon of the specified type"""
    weapon = Weapon(position, direction, module)
    return weapon