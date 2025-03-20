import pygame
import math
from game_config import *
from components.engine import Engine, ENGINE_BASIC
from components.weapon import create_weapon, LASER_BASIC
from components.hangar import Hangar, HANGAR_BASIC

class PlayerStats:
    """Class to store player stats that can be upgraded"""
    def __init__(self):
        # Ship stats
        self.hull_strength = 100
        self.max_hull = 100
        self.shield_strength = 0  # Can be upgraded later
        self.max_shield = 0
        
        # Energy stats
        self.energy = 100
        self.max_energy = 100
        self.energy_regen = 1  # Per second
        
        # Inventory stats
        self.max_slots = INVENTORY_COLS * INVENTORY_ROWS

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Stats
        self.stats = PlayerStats()
        
        # Components
        self.engine = Engine(ENGINE_BASIC)
        self.current_weapon = LASER_BASIC
        self.hangar = Hangar(HANGAR_BASIC)  # New hangar component
        
        # Try to load image or use triangle
        try:
            self.original_image = pygame.image.load("assets/ship.png").convert_alpha()
            # Scale to appropriate size (620x620 source image)
            scale_factor = 30 / 620
            new_size = int(620 * scale_factor)
            self.original_image = pygame.transform.scale(self.original_image, (new_size, new_size))
        except:
            # Create triangle if image not found
            self.original_image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, WHITE, [(15, 0), (0, 30), (30, 30)])
        
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.position = pygame.math.Vector2(self.rect.center)
        
        # Inventory - uses a 2D array of dicts to represent inventory grid
        self.inventory = []
        for _ in range(INVENTORY_ROWS):
            row = []
            for _ in range(INVENTORY_COLS):
                row.append({"type": None, "count": 0})
            self.inventory.append(row)
        
        self.total_ore = 0
        
        # Last time energy was regenerated
        self.last_energy_regen = pygame.time.get_ticks()
        
        # Add energy regeneration from hangar
        self.stats.energy_regen += self.hangar.get_power_output()
    
    def add_ore(self, ore_type):
        """Add an ore to inventory, finding an appropriate slot"""
        # Convert old ore type string to item object
        if isinstance(ore_type, str) and ore_type in ORE_TYPES:
            item = ORE_TYPES[ore_type]
        else:
            item = ore_type  # Already an item object
            
        # Find a slot for the ore
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot = self.inventory[row][col]
                # Add to existing stack of same type if not full
                if slot["item"] and slot["item"].name == item.name and slot["count"] < item.max_stack:
                    slot["count"] += 1
                    self.total_ore += 1
                    return True
        
        # Find empty slot if no existing stack has room
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot = self.inventory[row][col]
                if slot["item"] is None:  # Empty slot
                    slot["item"] = item
                    slot["count"] = 1
                    self.total_ore += 1
                    return True
        
        # Inventory full
        return False
    
    def update(self, game_state):
        # Skip updates if inventory is open
        if game_state != 0:  # GAME_RUNNING = 0
            return
            
        # Get key states
        keys = pygame.key.get_pressed()
        
        # Update engine and position
        self.position = self.engine.update(keys, self.position)
        
        # Update energy consumption from engine
        energy_usage = self.engine.get_energy_usage() / FPS
        self.stats.energy = max(0, self.stats.energy - energy_usage)
        
        # Regenerate energy over time
        current_time = pygame.time.get_ticks()
        if current_time - self.last_energy_regen > 1000:  # Every second
            self.stats.energy = min(self.stats.max_energy, 
                                   self.stats.energy + self.stats.energy_regen)
            self.last_energy_regen = current_time
        
        # Update image and rectangle
        self.image = pygame.transform.rotate(self.original_image, self.engine.get_angle())
        self.rect = self.image.get_rect(center=self.position)
    
    def shoot(self):
        """Create a weapon projectile if there's enough energy"""
        if self.stats.energy >= self.current_weapon.energy_cost:
            self.stats.energy -= self.current_weapon.energy_cost
            return create_weapon(self.current_weapon, self.position, self.engine.direction)
        return None
    
    def get_weapon_cooldown(self):
        """Return the cooldown time for the current weapon"""
        return self.current_weapon.cooldown
    
    def change_weapon(self, weapon_type):
        """Change to a different weapon type"""
        self.current_weapon = weapon_type
    
    def change_hangar(self, hangar_type):
        """Change to a different hangar type"""
        self.hangar.change_hangar(hangar_type)
        # Update energy regeneration based on new hangar
        self.stats.energy_regen = 1 + self.hangar.get_power_output()
    
    def add_ore(self, ore_type):
        """Add an ore to inventory, finding an appropriate slot"""
        # Find a slot for the ore
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot = self.inventory[row][col]
                # Add to existing stack of same type if not full
                if slot["type"] == ore_type and slot["count"] < MAX_STACK_SIZE:
                    slot["count"] += 1
                    self.total_ore += 1
                    return True
        
        # Find empty slot if no existing stack has room
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot = self.inventory[row][col]
                if slot["type"] is None:  # Empty slot
                    slot["type"] = ore_type
                    slot["count"] = 1
                    self.total_ore += 1
                    return True
        
        # Inventory full
        return False
    
    def get_ore_count(self, ore_type):
        """Count total of a specific ore type across all slots"""
        count = 0
        for row in self.inventory:
            for slot in row:
                if slot["type"] == ore_type:
                    count += slot["count"]
        return count
    
    def take_damage(self, amount):
        """Handle damage to shields and hull"""
        # Damage shields first if available
        if self.stats.shield_strength > 0:
            if amount <= self.stats.shield_strength:
                self.stats.shield_strength -= amount
                return False  # Not destroyed
            else:
                # Damage exceeds shields, apply remainder to hull
                remainder = amount - self.stats.shield_strength
                self.stats.shield_strength = 0
                self.stats.hull_strength -= remainder
        else:
            # No shields, damage hull directly
            self.stats.hull_strength -= amount
        
        # Check if destroyed
        return self.stats.hull_strength <= 0
    
    def get_inventory_capacity(self):
        """Return max and current inventory capacity"""
        total_slots = INVENTORY_COLS * INVENTORY_ROWS
        used_slots = 0
        
        for row in self.inventory:
            for slot in row:
                if slot["type"] is not None:
                    used_slots += 1
        
        return used_slots, total_slots