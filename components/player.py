import pygame
import math
from game_config import *
from components.engine import Engine, ENGINE_BASIC
from components.weapon import create_weapon, LASER_BASIC
from components.hangar import Hangar, HANGAR_BASIC
from components.module import *

class PlayerStats:
    """Player stats that can be upgraded"""
    def __init__(self):
        # Ship stats
        self.hull_strength = 100
        self.max_hull = 100
        self.shield_strength = 0
        self.max_shield = 0
        
        # Energy stats
        self.energy = 100
        self.max_energy = 100
        self.energy_regen = 1  # Per second
        
        # Inventory stats
        self.max_slots = INVENTORY_COLS * INVENTORY_ROWS
        
        # Currency
        self.silver = 50  # Starting silver

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Stats
        self.stats = PlayerStats()
        
        # Ship modules - use module system exclusively
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
        
        # Required components for gameplay
        self.engine = Engine(ENGINE_BASIC)
        self.current_weapon = LASER_BASIC
        self.hangar = Hangar(HANGAR_BASIC)
        
        # Update stats based on modules
        self.update_stats_from_modules()
        
        # Create player image
        try:
            self.original_image = pygame.image.load("assets/ship.png").convert_alpha()
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
        
        # Inventory
        self.inventory = []
        for _ in range(INVENTORY_ROWS):
            row = []
            for _ in range(INVENTORY_COLS):
                row.append({"item": None, "count": 0})
            self.inventory.append(row)
        
        self.total_ore = 0
        
        # Energy regen tracking
        self.last_energy_regen = pygame.time.get_ticks()
        
        # Active drones
        self.drones = []
    
    def update_stats_from_modules(self):
        """Update player stats based on installed modules"""
        # Reset stats to base values
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
        for aux_slot in ["aux1", "aux2"]:
            module = self.modules[aux_slot]
            if not module:
                continue
                
            # Energy cell
            if module.name == "Energy Cell":
                self.stats.max_energy += module.stats.get("energy_capacity", 0)
                self.stats.energy_regen += module.stats.get("recharge_boost", 0)
            # Shield booster
            elif module.name == "Shield Booster":
                shield_boost = module.stats.get("shield_boost", 0)
                self.stats.max_shield = int(self.stats.max_shield * (1 + shield_boost))
    
    def update(self, game_state):
        # Skip updates if not in gameplay state
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
            # Energy regen
            self.stats.energy = min(self.stats.max_energy, 
                                   self.stats.energy + self.stats.energy_regen)
            
            # Apply repair unit if equipped
            if self.modules["aux1"] and self.modules["aux1"].name == "Repair Unit":
                repair_rate = self.modules["aux1"].stats.get("repair_rate", 0)
                energy_cost = self.modules["aux1"].stats.get("energy_usage", 0)
                
                if self.stats.energy >= energy_cost and self.stats.hull_strength < self.stats.max_hull:
                    self.stats.hull_strength = min(self.stats.max_hull, 
                                                 self.stats.hull_strength + repair_rate)
                    self.stats.energy -= energy_cost
            
            # Apply shield regeneration
            if self.modules["shield"] and self.stats.shield_strength < self.stats.max_shield:
                regen_rate = self.modules["shield"].stats.get("regen_rate", 0)
                self.stats.shield_strength = min(self.stats.max_shield, 
                                              self.stats.shield_strength + regen_rate)
            
            self.last_energy_regen = current_time
        
        # Update image and rectangle
        self.image = pygame.transform.rotate(self.original_image, self.engine.get_angle())
        self.rect = self.image.get_rect(center=self.position)
    
    def shoot(self):
        """Create a weapon projectile if enough energy"""
        # Get weapon stats from module or fallback to legacy
        energy_cost = self.modules["weapon"].stats.get("energy_cost", self.current_weapon.energy_cost)
        
        if self.stats.energy >= energy_cost:
            self.stats.energy -= energy_cost
            return create_weapon(self.current_weapon, self.position, self.engine.direction)
        return None
    
    def get_weapon_cooldown(self):
        """Return cooldown time for current weapon"""
        return self.modules["weapon"].stats.get("cooldown", self.current_weapon.cooldown)
    
    def install_module(self, slot, module):
        """Install a module in the specified slot"""
        if slot in self.modules:
            self.modules[slot] = module
            self.update_stats_from_modules()
            
            # Update legacy components
            if slot == "engine":
                engine_type = self.modules[slot].stats.get("engine_type", ENGINE_BASIC)
                self.engine.change_engine(engine_type)
            elif slot == "hangar":
                hangar_type = self.modules[slot].stats.get("hangar_type", HANGAR_BASIC)
                self.hangar.change_hangar(hangar_type)
            
            return True
        return False
    
    def add_ore(self, item):
        """Add item to inventory"""
        # Find slot with same item that isn't full
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot = self.inventory[row][col]
                # Add to existing stack if not full
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
        used_slots = sum(1 for row in self.inventory for slot in row if slot["item"] is not None)
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
    
    def sync_modules_with_components(self):
        """Sync module system with legacy components"""
        # Update engine component
        if self.modules["engine"]:
            engine_stats = self.modules["engine"].stats
            engine_type = ENGINE_BASIC
            # Set engine parameters from module stats
            engine_type.max_speed = engine_stats.get("max_speed", 5.0)
            engine_type.acceleration = engine_stats.get("acceleration", 0.2)
            engine_type.turn_rate = engine_stats.get("turn_rate", 3.0)
            engine_type.energy_usage = engine_stats.get("energy_usage", 1)
            self.engine.change_engine(engine_type)
        
        # Update weapon component
        if self.modules["weapon"]:
            weapon_stats = self.modules["weapon"].stats
            # Apply weapon stats to current_weapon
            self.current_weapon.damage = weapon_stats.get("damage", 1)
            self.current_weapon.speed = weapon_stats.get("speed", 10)
            self.current_weapon.cooldown = weapon_stats.get("cooldown", 300)
            self.current_weapon.energy_cost = weapon_stats.get("energy_cost", 1)