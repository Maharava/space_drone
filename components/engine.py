import pygame
import math
from game_config import *

class Engine:
    """Engine class for controlling ship movement"""
    def __init__(self, module=None):
        self.module = module
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(0, -1)  # Default pointing up
        self.angle = 0
        self.thrusting = False
        self.energy_usage = 0
    
    def get_module_stat(self, stat_name, default_value):
        """Helper to get a stat from the module"""
        if self.module and hasattr(self.module, 'stats') and stat_name in self.module.stats:
            return self.module.stats[stat_name]
        return default_value
    
    def update(self, keys, position):
        """Update engine state based on key presses"""
        self.thrusting = False
        
        # Get engine stats from module
        max_speed = self.get_module_stat('max_speed', 5.0)
        acceleration = self.get_module_stat('acceleration', 0.2)
        turn_rate = self.get_module_stat('turn_rate', 3.0)
        energy_usage = self.get_module_stat('energy_usage', 1)
        
        # Rotate
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += turn_rate
            self.direction.rotate_ip(-turn_rate)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= turn_rate
            self.direction.rotate_ip(turn_rate)
        
        # Calculate forward vector
        forward = pygame.math.Vector2(self.direction)
        
        # Apply acceleration when keys are pressed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity += forward * acceleration
            self.thrusting = True
            self.energy_usage = energy_usage
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity -= forward * acceleration
            self.thrusting = True
            self.energy_usage = energy_usage
        else:
            # No movement keys pressed - gradually stop
            if self.velocity.length() > 0:
                # Apply deceleration
                deceleration = min(acceleration * 0.8, self.velocity.length())
                self.velocity *= (1 - deceleration)
                
                # Stop completely if very slow
                if self.velocity.length() < 0.1:
                    self.velocity = pygame.math.Vector2(0, 0)
            
            self.energy_usage = 0
        
        # Limit speed
        speed = self.velocity.length()
        if speed > max_speed:
            self.velocity.scale_to_length(max_speed)
        
        # Update position
        new_position = position + self.velocity
        
        # Limit to world boundaries
        new_position.x = max(0, min(WORLD_WIDTH, new_position.x))
        new_position.y = max(0, min(WORLD_HEIGHT, new_position.y))
        
        return new_position
    
    def get_angle(self):
        """Return the current angle"""
        return self.angle
    
    def is_thrusting(self):
        """Return whether the engine is currently thrusting"""
        return self.thrusting
    
    def get_energy_usage(self):
        """Return the current energy usage"""
        return self.energy_usage

    def change_engine(self, module):
        """Change to a different engine module"""
        self.module = module