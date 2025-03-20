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
        # Check respawn queue and spawn new asteroids
        for i in range(len(cls.respawn_queue) - 1, -1, -1):
            asteroid_data = cls.respawn_queue[i]
            asteroid_data["timer"] -= 1
            
            if asteroid_data["timer"] <= 0:
                # Respawn at a random edge
                new_asteroid = Asteroid(asteroid_type=asteroid_data["type"])
                
                # Choose a random edge (0=top, 1=right, 2=bottom, 3=left)
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
        # Asteroid type affects ore drops
        self.asteroid_type = asteroid_type
        
        # Choose from 5 predefined sizes between 32x32 and 96x96
        size_options = [32, 48, 64, 80, 96]
        self.size = random.choice(size_options)
        
        # Choose one of five random asteroid images
        asteroid_num = random.randint(1, 5)
        
        try:
            # Try to load one of the 5 asteroid images
            image_path = f"assets/asteroid_{asteroid_num}.png"
            self.original_image = pygame.image.load(image_path).convert_alpha()
            # Scale properly assuming 480x480 source image
            scale_factor = self.size / 480
            new_size = int(480 * scale_factor)
            self.original_image = pygame.transform.scale(self.original_image, (new_size, new_size))
        except:
            # Create circle if image not found
            self.original_image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, GREY, (self.size // 2, self.size // 2), self.size // 2)
        
        # Set up rotation properties
        self.angle = 0
        self.rotation_speed = random.uniform(0.1, 0.5)  # Slow rotation, varying speeds
        if random.random() < 0.5:  # 50% chance to rotate counterclockwise
            self.rotation_speed *= -1
            
        # Start with unrotated image
        self.image = self.original_image.copy()
        
        # Random position anywhere in the world
        x = random.randint(50, WORLD_WIDTH - 50)
        y = random.randint(50, WORLD_HEIGHT - 50)
                
        self.rect = self.image.get_rect(center=(x, y))
        self.position = pygame.math.Vector2(self.rect.center)
        self.health = self.size // 10  # Health based on size
        
        # Random very slow movement
        angle = random.uniform(0, math.pi * 2)
        self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        self.speed = random.uniform(0.1, 0.3)  # Greatly reduced speed
    
    def update(self, game_state):
        # Skip updates if inventory is open
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
        
        # Update rotation
        self.angle += self.rotation_speed
        if self.angle >= 360:
            self.angle -= 360
        elif self.angle < 0:
            self.angle += 360
            
        # Rotate image and update rect
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)
    
    def damage(self, amount=1):
        self.health -= amount
        return self.health <= 0
    
    def schedule_respawn(self, time_frames):
        """Add this asteroid to the respawn queue"""
        Asteroid.respawn_queue.append({
            "type": self.asteroid_type,
            "timer": time_frames
        })
    
    def get_ore_drops(self):
        """Returns a list of ores dropped by this asteroid based on type"""
        # Size determines how many ore pieces drop
        drops = []
        
        # Base number of drops based on size
        drop_count = max(1, self.size // 16)
        
        # Adjust drop count based on asteroid type
        if self.asteroid_type == "rich":
            # Rich asteroids give 25% more ore
            drop_count = int(drop_count * 1.25)
            drop_count = max(2, drop_count)  # Minimum 2 drops for rich
        elif self.asteroid_type == "dry":
            # Dry asteroids give 25% less ore
            drop_count = int(drop_count * 0.75)
            drop_count = max(1, drop_count)  # Minimum 1 drop
        
        # Add random variation
        drop_count += random.randint(-1, 2)
        drop_count = max(1, drop_count)  # Minimum 1 drop
        
        for _ in range(drop_count):
            # Get ore type based on asteroid type
            drops.append(self._determine_ore_type())
        
        return drops
    
    def _determine_ore_type(self):
        """Determine ore type based on asteroid type and random chance"""
        roll = random.random()
        
        # Different ore distributions based on asteroid type
        if self.asteroid_type == "rich":
            # Rich asteroids have better chances for rare materials
            if roll < 0.4:
                return "low-grade"  # 40% chance (reduced)
            elif roll < 0.7:
                return "high-grade"  # 30% chance (increased)
            elif roll < 0.9:
                return "rare-ore"    # 20% chance (increased)
            else:
                return "silver"      # 10% chance (increased)
                
        elif self.asteroid_type == "dry":
            # Dry asteroids have no silver and very little rare ore
            if roll < 0.7:
                return "low-grade"   # 70% chance (increased)
            elif roll < 0.95:
                return "high-grade"  # 25% chance (reduced)
            else:
                return "rare-ore"    # 5% chance (reduced)
                                     # 0% chance for silver
                
        else:  # Regular asteroid
            # Standard distribution
            if roll < 0.5:
                return "low-grade"   # 50% chance
            elif roll < 0.8:
                return "high-grade"  # 30% chance
            elif roll < 0.95:
                return "rare-ore"    # 15% chance
            else:
                return "silver"      # 5% chance