import pygame
import math
from game_config import *
from components.engine import Engine, ENGINE_BASIC
from components.weapon import create_weapon, LASER_BASIC
from components.hangar import Hangar, HANGAR_BASIC
from components.module import *

class PlayerStats:
    """Class to store player stats that can be upgraded"""
    def __init__(self):
        # Ship stats
        self.hull_strength = 100
        self.max_hull = 100
        self.shield_strength = 0  # Updated by modules
        self.max_shield = 0
        
        # Energy stats
        self.energy = 100
        self.max_energy = 100
        self.energy_regen = 1  # Per second
        
        # Inventory stats
        self.max_slots = INVENTORY_COLS * INVENTORY_ROWS
        
        # Currency
        self.silver = 50  # Start with a small amount of silver

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Stats
        self.stats = PlayerStats()
        
        # Ship modules
        self.modules = {
            "engine": ENGINE_BASIC,
            "shield": SHIELD_BASIC,
            "weapon": WEAPON_BASIC_LASER,
            "scanner": SCANNER_BASIC,
            "facility": FACILITY_BASIC,
            "jump_engine": JUMP_ENGINE_BASIC,
            "hangar": HANGAR_BASIC,
            "aux1": None,
            "aux2": None
        }
        
        # Legacy components - to be removed after module system fully integrated
        self.engine = Engine(ENGINE_BASIC)
        self.current_weapon = LASER_BASIC
        self.hangar = Hangar(HANGAR_BASIC)
        
        # Apply module effects to stats
        self.update_stats_from_modules()
        
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
                row.append({"item": None, "count": 0})
            self.inventory.append(row)
        
        self.total_ore = 0
        
        # Last time energy was regenerated
        self.last_energy_regen = pygame.time.get_ticks()
        
        # Active drones list
        self.drones = []
    
    def update_stats_from_modules(self):
        """Update player stats based on installed modules"""
        # Reset some stats to base values
        self.stats.max_shield = 0
        self.stats.shield_strength = 0
        self.stats.energy_regen = 1
        
        # Apply shield module
        if self.modules["shield"]:
            self.stats.max_shield = self.modules["shield"].stats.get("capacity", 0)
            self.stats.shield_strength = self.stats.max_shield
        
        # Apply hangar energy boost
        if self.modules["hangar"]:
            self.stats.energy_regen += self.modules["hangar"].stats.get("energy_output", 0)
        
        # Apply auxiliary modules
        if self.modules["aux1"]:
            # Energy cell
            if self.modules["aux1"].name == "Energy Cell":
                self.stats.max_energy += self.modules["aux1"].stats.get("energy_capacity", 0)
                self.stats.energy_regen += self.modules["aux1"].stats.get("recharge_boost", 0)
            # Shield booster
            elif self.modules["aux1"].name == "Shield Booster":
                shield_boost = self.modules["aux1"].stats.get("shield_boost", 0)
                self.stats.max_shield = int(self.stats.max_shield * (1 + shield_boost))
            # Repair unit - implemented in update method
        
        if self.modules["aux2"]:
            # Apply second auxiliary module effects similar to aux1
            pass
    
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
            
            # Apply repair unit effect if equipped
            if self.modules["aux1"] and self.modules["aux1"].name == "Repair Unit":
                repair_rate = self.modules["aux1"].stats.get("repair_rate", 0)
                energy_cost = self.modules["aux1"].stats.get("energy_usage", 0)
                
                if self.stats.energy >= energy_cost and self.stats.hull_strength < self.stats.max_hull:
                    self.stats.hull_strength = min(self.stats.max_hull, 
                                                 self.stats.hull_strength + repair_rate)
                    self.stats.energy -= energy_cost
            
            # Apply shield regeneration if shield module equipped
            if self.modules["shield"] and self.stats.shield_strength < self.stats.max_shield:
                regen_rate = self.modules["shield"].stats.get("regen_rate", 0)
                self.stats.shield_strength = min(self.stats.max_shield, 
                                              self.stats.shield_strength + regen_rate)
            
            self.last_energy_regen = current_time
        
        # Update image and rectangle
        self.image = pygame.transform.rotate(self.original_image, self.engine.get_angle())
        self.rect = self.image.get_rect(center=self.position)
    
    def shoot(self):
        """Create a weapon projectile if there's enough energy"""
        weapon = self.current_weapon  # Legacy
        
        # Use module weapon stats if available
        if self.modules["weapon"]:
            energy_cost = self.modules["weapon"].stats.get("energy_cost", 1)
        else:
            energy_cost = weapon.energy_cost
        
        if self.stats.energy >= energy_cost:
            self.stats.energy -= energy_cost
            return create_weapon(weapon, self.position, self.engine.direction)
        return None
    
    def get_weapon_cooldown(self):
        """Return the cooldown time for the current weapon"""
        # Use module weapon stats if available
        if self.modules["weapon"]:
            return self.modules["weapon"].stats.get("cooldown", 300)
        return self.current_weapon.cooldown
    
    def install_module(self, slot, module):
        """Install a module in the specified slot"""
        if slot in self.modules:
            self.modules[slot] = module
            
            # Update stats after installing a new module
            self.update_stats_from_modules()
            
            # Legacy support until full module system implemented
            if slot == "weapon":
                self.current_weapon = LASER_BASIC  # Should be updated based on module
            elif slot == "engine":
                self.engine.change_engine(ENGINE_BASIC)  # Should be updated based on module
            elif slot == "hangar":
                self.hangar.change_hangar(HANGAR_BASIC)  # Should be updated based on module
            
            return True
        return False
    
    def add_ore(self, item):
        """Add an item to inventory, finding an appropriate slot"""
        # Find a slot with the same item that isn't full
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
    
    def get_inventory_capacity(self):
        """Return max and current inventory capacity"""
        total_slots = INVENTORY_COLS * INVENTORY_ROWS
        used_slots = 0
        
        for row in self.inventory:
            for slot in row:
                if slot["item"] is not None:
                    used_slots += 1
        
        return used_slots, total_slots
    
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