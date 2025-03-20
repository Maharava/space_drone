import pygame
import math
from game_config import *

class EngineType:
    """Class to define different engine types"""
    def __init__(self, name, max_speed, acceleration, turn_rate, energy_usage):
        self.name = name
        self.max_speed = max_speed
        self.acceleration = acceleration
        self.turn_rate = turn_rate  # Degrees per frame
        self.energy_usage = energy_usage  # Energy used per second of thrust

# Define standard engine types
ENGINE_BASIC = EngineType("Basic Engine", 5.0, 0.2, 3.0, 1)
ENGINE_SPEEDY = EngineType("Speedy Engine", 7.0, 0.25, 2.5, 2)
ENGINE_AGILE = EngineType("Agile Engine", 4.5, 0.15, 4.5, 1.5)
ENGINE_HEAVY = EngineType("Heavy Engine", 3.5, 0.1, 2.0, 0.8)

class Engine:
    """Engine class for controlling ship movement"""
    def __init__(self, engine_type=ENGINE_BASIC):
        self.engine_type = engine_type
        self.velocity = pygame.math.Vector2(0, 0)
        self.direction = pygame.math.Vector2(0, -1)  # Default pointing up
        self.angle = 0
        self.thrusting = False
        self.energy_usage = 0
    
    def update(self, keys, position):
        """Update engine state based on key presses"""
        self.thrusting = False
        
        # Rotate
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle += self.engine_type.turn_rate
            self.direction.rotate_ip(-self.engine_type.turn_rate)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle -= self.engine_type.turn_rate
            self.direction.rotate_ip(self.engine_type.turn_rate)
        
        # Calculate forward vector
        forward = pygame.math.Vector2(self.direction)
        
        # Apply acceleration when keys are pressed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.velocity += forward * self.engine_type.acceleration
            self.thrusting = True
            self.energy_usage = self.engine_type.energy_usage
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.velocity -= forward * self.engine_type.acceleration
            self.thrusting = True
            self.energy_usage = self.engine_type.energy_usage
        else:
            # No movement keys pressed - gradually stop
            if self.velocity.length() > 0:
                # Apply deceleration
                deceleration = min(self.engine_type.acceleration * 0.8, self.velocity.length())
                self.velocity *= (1 - deceleration)
                
                # Stop completely if very slow
                if self.velocity.length() < 0.1:
                    self.velocity = pygame.math.Vector2(0, 0)
            
            self.energy_usage = 0
        
        # Limit speed
        speed = self.velocity.length()
        if speed > self.engine_type.max_speed:
            self.velocity.scale_to_length(self.engine_type.max_speed)
        
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

    def change_engine(self, engine_type):
        """Change to a different engine type"""
        self.engine_type = engine_type
