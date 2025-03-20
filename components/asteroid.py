import pygame
import random
import math
from game_config import *
from components.items import ORE_TYPES

class Asteroid(pygame.sprite.Sprite):
    # Track destroyed asteroids for respawning
    respawn_queue = []
    
    @classmethod
    def update_respawns(cls, all_sprites, asteroids_group):
        # Process respawn queue
        for i in range(len(cls.respawn_queue) - 1, -1, -1):
            asteroid_data = cls.respawn_queue[i]
            asteroid_data["timer"] -= 1
            
            if asteroid_data["timer"] <= 0:
                # Respawn at random edge
                new_asteroid = Asteroid(asteroid_type=asteroid_data["type"])
                
                # Choose edge (0=top, 1=right, 2=bottom, 3=left)
                edge = random.randint(0, 3)
                if edge == 0:  # Top
                    x = random.randint(0, WORLD_WIDTH)
                    y = 0
                elif edge == 1:  # Right
                    x = WORLD_WIDTH
                    y = random.randint(0, WORLD_HEIGHT)
                elif edge == 2:  # Bottom
                    x = random.randint(0, WORLD_WIDTH)
                    y = WORLD_HEIGHT
                else:  # Left
                    x = 0
                    y = random.randint(0, WORLD_HEIGHT)
                
                # Set position
                new_asteroid.rect.center = (x, y)
                new_asteroid.position = pygame.math.Vector2(new_asteroid.rect.center)
                
                # Add to sprite groups
                all_sprites.add(new_asteroid)
                asteroids_group.add(new_asteroid)
                
                # Remove from queue
                cls.respawn_queue.pop(i)
    
    def __init__(self, asteroid_type="regular"):
        super().__init__()
        # Set asteroid type (affects ore drops)
        self.asteroid_type = asteroid_type
        
        # Choose from predefined sizes
        size_options = [32, 48, 64, 80, 96]
        self.size = random.choice(size_options)
        
        # Choose random asteroid image (1-5)
        asteroid_num = random.randint(1, 5)
        
        try:
            # Try loading asteroid image
            self.original_image = pygame.image.load(f"assets/asteroid_{asteroid_num}.png").convert_alpha()
            scale_factor = self.size / 480  # Assuming 480x480 source image
            new_size = int(480 * scale_factor)
            self.original_image = pygame.transform.scale(self.original_image, (new_size, new_size))
        except:
            # Fallback to circle if image not found
            self.original_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, GREY, (self.size // 2, self.size // 2), self.size // 2)
        
        # Set fixed random rotation angle
        self.angle = random.randint(0, 359)
        
        # Apply the rotation once
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        
        # Random position
        x = random.randint(50, WORLD_WIDTH - 50)
        y = random.randint(50, WORLD_HEIGHT - 50)
                
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(self.rect.center)
        self.health = self.size // 10  # Health based on size
        
        # Slow random movement
        angle = random.uniform(0, math.pi * 2)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = random.uniform(0.1, 0.3)
    
    def update(self, game_state):
        # Skip updates if not in gameplay state
        if game_state != 0:  # GAME_RUNNING = 0
            return
        
        # Update position
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
        
        # Update rect position without rotating again
        self.rect.center = self.position
    
    def damage(self, amount=1):
        self.health -= amount
        return self.health <= 0
    
    def schedule_respawn(self, time_frames):
        """Add to respawn queue"""
        Asteroid.respawn_queue.append({
            "type": self.asteroid_type,
            "timer": time_frames
        })
    
    def get_ore_drops(self):
        """Returns ore items dropped by asteroid"""
        # Number of drops based on size
        drops = []
        
        # Base drops from size
        drop_count = max(1, self.size // 16)
        
        # Adjust by asteroid type
        if self.asteroid_type == "rich":
            drop_count = max(2, int(drop_count * 1.25))  # Rich = 25% more, min 2
        elif self.asteroid_type == "dry":
            drop_count = max(1, int(drop_count * 0.75))  # Dry = 25% less, min 1
        
        # Add variation
        drop_count += random.randint(-1, 2)
        drop_count = max(1, drop_count)  # Minimum 1 drop
        
        # Get ore drops
        for _ in range(drop_count):
            ore_type = self._determine_ore_type()
            drops.append(ORE_TYPES[ore_type])
        
        return drops
    
    def _determine_ore_type(self):
        """Determine ore type based on asteroid type"""
        roll = random.random()
        
        # Different distributions by asteroid type
        if self.asteroid_type == "rich":
            # Rich asteroids have better rare materials
            if roll < 0.4:
                return "low-grade"    # 40%
            elif roll < 0.7:
                return "high-grade"   # 30%
            elif roll < 0.9:
                return "rare-ore"     # 20%
            else:
                return "silver"       # 10%
                
        elif self.asteroid_type == "dry":
            # Dry asteroids have no silver and less rare ore
            if roll < 0.7:
                return "low-grade"    # 70%
            elif roll < 0.95:
                return "high-grade"   # 25%
            else:
                return "rare-ore"     # 5%
                
        else:  # Regular asteroid
            # Standard distribution
            if roll < 0.5:
                return "low-grade"    # 50%
            elif roll < 0.8:
                return "high-grade"   # 30%
            elif roll < 0.95:
                return "rare-ore"     # 15%
            else:
                return "silver"       # 5%