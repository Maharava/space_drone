import pygame
import math
from game_config import *
from components.weapon import create_weapon, LASER_BASIC

class DroneStats:
    def __init__(self, speed=3.0, agility=2.0, shield=30, max_shield=30, hull=50, max_hull=50, weapon=LASER_BASIC, energy=50, max_energy=50, energy_regen=0.5):
        self.speed = speed
        self.agility = agility
        self.shield = shield
        self.max_shield = max_shield
        self.hull = hull
        self.max_hull = max_hull
        self.weapon = weapon
        self.energy = energy
        self.max_energy = max_energy
        self.energy_regen = energy_regen

class Drone(pygame.sprite.Sprite):
    def __init__(self, drone_type="scout", position=None, owner=None):
        super().__init__()
        self.drone_type = drone_type
        self.owner = owner
        
        # Initialize stats based on drone type
        if drone_type == "scout":
            self.stats = DroneStats(speed=4.0, agility=3.0, shield=20, max_shield=20, hull=30, max_hull=30)
        elif drone_type == "fighter":
            self.stats = DroneStats(speed=3.5, agility=2.5, shield=40, max_shield=40, hull=60, max_hull=60)
        elif drone_type == "miner":
            self.stats = DroneStats(speed=2.5, agility=1.5, shield=30, max_shield=30, hull=70, max_hull=70)
        else:
            # Default stats
            self.stats = DroneStats()
        
        # Try to load drone image or use a default shape
        try:
            self.original_image = pygame.image.load(f"assets/drone_{drone_type}.png").convert_alpha()
            # Scale to appropriate size (assume 320x320 source image)
            scale_factor = 20 / 320  # Drones are smaller than the player
            new_size = int(320 * scale_factor)
            self.original_image = pygame.transform.scale(self.original_image, (new_size, new_size))
        except:
            # Create simple drone shape
            self.original_image = pygame.Surface((20, 20), pygame.SRCALPHA)
            if drone_type == "scout":
                color = BLUE
            elif drone_type == "fighter":
                color = RED
            elif drone_type == "miner":
                color = GREEN
            else:
                color = YELLOW
                
            # Draw a simple triangle shape
            pygame.draw.polygon(self.original_image, color, [(10, 0), (0, 20), (20, 20)])
        
        self.image = self.original_image
        
        # Set initial position
        if position:
            self.position = pygame.math.Vector2(position)
        elif owner:
            # Position near the owner
            offset = pygame.math.Vector2(30, 0).rotate(random.randint(0, 360))
            self.position = pygame.math.Vector2(owner.position) + offset
        else:
            # Random position
            self.position = pygame.math.Vector2(random.randint(100, WORLD_WIDTH-100), 
                                              random.randint(100, WORLD_HEIGHT-100))
        
        self.rect = self.image.get_rect(center=self.position)
        self.direction = pygame.math.Vector2(0, -1)  # Default pointing up
        self.angle = 0
        
        # Movement variables
        self.velocity = pygame.math.Vector2(0, 0)
        self.target_position = None
        self.state = "idle"  # idle, following, mining, attacking
        self.last_shot_time = 0
        
        # Energy regeneration
        self.last_energy_regen = pygame.time.get_ticks()
    
    def update(self, game_state):
        # Skip updates if not in game running state
        if game_state != 0:  # GAME_RUNNING = 0
            return
        
        # Energy regeneration
        current_time = pygame.time.get_ticks()
        if current_time - self.last_energy_regen > 1000:  # Every second
            self.stats.energy = min(self.stats.max_energy, 
                                  self.stats.energy + self.stats.energy_regen)
            self.last_energy_regen = current_time
        
        # Simple AI behavior based on state
        if self.state == "following" and self.owner:
            self.follow_owner()
        elif self.state == "mining" and self.target_position:
            self.move_to_target()
        elif self.state == "attacking" and self.target_position:
            self.attack_target()
        else:
            # Idle behavior - small random movement
            if random.random() < 0.02:  # 2% chance to change direction
                angle = random.uniform(0, math.pi * 2)
                self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 0.5
        
        # Apply velocity
        self.position += self.velocity
        
        # Keep drone within world boundaries
        self.position.x = max(0, min(WORLD_WIDTH, self.position.x))
        self.position.y = max(0, min(WORLD_HEIGHT, self.position.y))
        
        # Update angle based on movement direction
        if self.velocity.length() > 0.1:
            self.direction = self.velocity.normalize()
            # Calculate angle in degrees (0 degrees is up, increases clockwise)
            self.angle = math.degrees(math.atan2(-self.direction.x, -self.direction.y))
        
        # Update image and rectangle
        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.position)
    
    def follow_owner(self):
        """Follow the owner at a distance"""
        if not self.owner:
            return
            
        # Calculate vector to owner
        to_owner = pygame.math.Vector2(self.owner.position) - self.position
        distance = to_owner.length()
        
        if distance > 80:  # Follow distance
            # Move towards owner
            direction = to_owner.normalize()
            self.velocity = direction * self.stats.speed
        elif distance < 40:  # Too close
            # Move away from owner
            direction = -to_owner.normalize()
            self.velocity = direction * self.stats.speed * 0.5
        else:
            # Maintain distance - small random movement
            if random.random() < 0.05:  # 5% chance to adjust position
                angle = random.uniform(0, math.pi * 2)
                self.velocity = pygame.math.Vector2(math.cos(angle), math.sin(angle)) * 0.8
    
    def move_to_target(self):
        """Move towards a target position"""
        if not self.target_position:
            return
            
        # Calculate vector to target
        to_target = self.target_position - self.position
        distance = to_target.length()
        
        if distance > 10:  # Not at target yet
            # Move towards target
            direction = to_target.normalize()
            self.velocity = direction * self.stats.speed
        else:
            # Reached target
            self.velocity = pygame.math.Vector2(0, 0)
            self.state = "idle"
    
    def attack_target(self):
        """Move towards and attack a target"""
        if not self.target_position:
            return
            
        # Calculate vector to target
        to_target = self.target_position - self.position
        distance = to_target.length()
        
        if distance > 150:  # Too far to attack
            # Move towards target
            direction = to_target.normalize()
            self.velocity = direction * self.stats.speed
        elif distance < 80:  # Too close
            # Back up a bit
            direction = -to_target.normalize()
            self.velocity = direction * self.stats.speed * 0.5
        else:
            # In attack range - orbit the target
            orbit_direction = pygame.math.Vector2(-to_target.y, to_target.x).normalize()
            self.velocity = orbit_direction * self.stats.speed * 0.7
            
            # Try to shoot
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.stats.weapon.cooldown:
                # Would shoot here in the future
                self.last_shot_time = current_time
    
    def take_damage(self, amount):
        """Handle damage to shields and hull"""
        # Damage shields first if available
        if self.stats.shield > 0:
            if amount <= self.stats.shield:
                self.stats.shield -= amount
                return False  # Not destroyed
            else:
                # Damage exceeds shields, apply remainder to hull
                remainder = amount - self.stats.shield
                self.stats.shield = 0
                self.stats.hull -= remainder
        else:
            # No shields, damage hull directly
            self.stats.hull -= amount
        
        # Check if destroyed
        return self.stats.hull <= 0
    
    def set_state(self, new_state, target=None):
        """Set the drone's state and target"""
        self.state = new_state
        
        if target:
            if isinstance(target, pygame.sprite.Sprite):
                self.target_position = pygame.math.Vector2(target.rect.center)
            else:
                self.target_position = pygame.math.Vector2(target)