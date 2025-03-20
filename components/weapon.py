import pygame
from game_config import *

class WeaponType:
    """Class to define different weapon types"""
    def __init__(self, name, damage, speed, cooldown, color, size, energy_cost=0):
        self.name = name
        self.damage = damage
        self.speed = speed
        self.cooldown = cooldown  # milliseconds
        self.color = color
        self.size = size
        self.energy_cost = energy_cost

# Define standard weapon types
LASER_BASIC = WeaponType("Basic Laser", 1, 10, 300, RED, (5, 5), 1)
LASER_RAPID = WeaponType("Rapid Laser", 0.5, 12, 150, GREEN, (3, 7), 1)
LASER_HEAVY = WeaponType("Heavy Laser", 3, 8, 500, BLUE, (8, 8), 3)
MISSILE = WeaponType("Missile", 5, 6, 800, YELLOW, (8, 12), 5)

class Weapon(pygame.sprite.Sprite):
    """Base class for all weapon projectiles"""
    def __init__(self, position, direction, weapon_type):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2(direction)
        self.weapon_type = weapon_type
        
        # Create sprite
        self.image = pygame.Surface(weapon_type.size)
        self.image.fill(weapon_type.color)
        self.rect = self.image.get_rect(center=position)
    
    def update(self, game_state):
        """Update position and check bounds"""
        # Skip updates if inventory is open
        if game_state != 0:  # GAME_RUNNING = 0
            return
        
        self.position += self.direction * self.weapon_type.speed
        self.rect.center = self.position
        
        # Remove if off world
        if (self.position.x < 0 or self.position.x > WORLD_WIDTH or 
            self.position.y < 0 or self.position.y > WORLD_HEIGHT):
            self.kill()

# Factory function to create weapons
def create_weapon(weapon_type, position, direction):
    """Create a weapon of the specified type"""
    return Weapon(position, direction, weapon_type)