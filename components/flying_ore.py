import pygame
import random
import math
from game_config import *

class FlyingOre(pygame.sprite.Sprite):
    """Visual representation of ore flying towards the player after destroying an asteroid"""
    def __init__(self, position, ore_type, target_entity):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        self.ore_type = ore_type
        self.target = target_entity
        
        # Create visual based on ore type
        self.size = 10  # Small ore fragment
        
        # Try to load image or use circle
        try:
            self.image = pygame.image.load(f"assets/{ore_type}.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.size, self.size))
        except:
            # Create circle if image not found
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            
            # Color based on ore type
            if ore_type == "low-grade":
                color = BROWN
            elif ore_type == "high-grade":
                color = YELLOW
            elif ore_type == "rare-ore":
                color = PURPLE
            elif ore_type == "silver":
                color = SILVER
            else:
                color = WHITE
            
            pygame.draw.circle(self.image, color, (self.size // 2, self.size // 2), self.size // 2)
        
        self.rect = self.image.get_rect(center=position)
        
        # Movement parameters
        self.speed = random.uniform(4.0, 7.0)  # Faster than regular objects
        self.collected = False
        
        # Generate a curved path
        self.generate_curved_path()
        
        # Life timer to prevent orphaned ores (will be collected before this expires)
        self.life_timer = 180  # 3 seconds at 60 FPS
        
    def generate_curved_path(self):
        """Generate a curved path towards the player"""
        # Create a bezier curve control point
        target_vec = pygame.math.Vector2(self.target.rect.center) - self.position
        
        # Perpendicular vector for curve control
        perp = pygame.math.Vector2(-target_vec.y, target_vec.x)
        perp.normalize_ip()
        
        # Scale perpendicular based on distance (more curve for longer distances)
        distance = target_vec.length()
        curve_strength = min(distance * 0.5, 200)  # Cap maximum curve
        
        # Random curve direction and magnitude
        curve_magnitude = random.uniform(0.1, 1.0) * curve_strength
        if random.random() < 0.5:
            curve_magnitude *= -1
            
        self.control_point = self.position + perp * curve_magnitude
        
        # Curve progress
        self.curve_t = 0.0
        
        # Store initial position and target for bezier calculation
        self.start_pos = pygame.math.Vector2(self.position)
        self.target_pos = pygame.math.Vector2(self.target.rect.center)
    
    def update(self, game_state):
        """Update the ore's position along its path"""
        # Skip updates if inventory is open
        if game_state != 0:  # GAME_RUNNING = 0
            return
        
        # Decrement life timer
        self.life_timer -= 1
        if self.life_timer <= 0:
            self.kill()
            return
            
        # Update target position in case target moves
        self.target_pos = pygame.math.Vector2(self.target.rect.center)
        
        # Move along bezier curve
        self.curve_t += 0.02 * self.speed  # Adjust speed via t increment
        
        # Clamp t to [0, 1]
        if self.curve_t >= 1.0:
            self.curve_t = 1.0
        
        # Quadratic bezier curve: B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
        t = self.curve_t
        one_minus_t = 1 - t
        
        # Calculate new position
        self.position.x = (one_minus_t**2 * self.start_pos.x + 
                          2 * one_minus_t * t * self.control_point.x + 
                          t**2 * self.target_pos.x)
        
        self.position.y = (one_minus_t**2 * self.start_pos.y + 
                          2 * one_minus_t * t * self.control_point.y + 
                          t**2 * self.target_pos.y)
        
        # Update rectangle position
        self.rect.center = self.position
        
        # Check if ore has reached the player
        if self.rect.colliderect(self.target.rect):
            # Add ore to player inventory
            self.target.add_ore(self.ore_type)
            self.kill()
