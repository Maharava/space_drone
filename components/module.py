import pygame
from utils import load_image

class Module:
    def __init__(self, name, description, value, stats=None):
        self.name = name
        self.description = description
        self.value = value
        self.stats = stats or {}
        self.image = None
    
    def get_image(self, size=40):
        """Get properly sized module image"""
        if not self.image or self.image.get_width() != size:
            self.image = load_image(self.name, size=size, prefix="module_", 
                                  fallback_color=(100, 100, 150))
        return self.image

# Engine modules
ENGINE_BASIC = Module(
    "Basic Engine", 
    "Standard engine with moderate speed and acceleration.",
    value=200,
    stats={"max_speed": 5.0, "acceleration": 0.2, "turn_rate": 3.0, "energy_usage": 1}
)

ENGINE_SPEEDY = Module(
    "Speedy Engine", 
    "Faster engine with higher energy consumption.",
    value=500, 
    stats={"max_speed": 7.0, "acceleration": 0.25, "turn_rate": 2.5, "energy_usage": 2}
)

ENGINE_AGILE = Module(
    "Agile Engine", 
    "Highly maneuverable engine with moderate speed.",
    value=400, 
    stats={"max_speed": 4.5, "acceleration": 0.15, "turn_rate": 4.5, "energy_usage": 1.5}
)

# Shield modules
SHIELD_BASIC = Module(
    "Basic Shield", 
    "Standard shield providing moderate protection.",
    value=250, 
    stats={"capacity": 50, "regen_rate": 0.5}
)

SHIELD_REINFORCED = Module(
    "Reinforced Shield", 
    "Higher capacity shield with slower regeneration.",
    value=500, 
    stats={"capacity": 100, "regen_rate": 0.3}
)

SHIELD_QUICK = Module(
    "Quick Shield", 
    "Faster regenerating shield with lower capacity.",
    value=350, 
    stats={"capacity": 30, "regen_rate": 1.0}
)

# Weapon modules
WEAPON_BASIC_LASER = Module(
    "Basic Laser", 
    "Standard laser with balanced stats.",
    value=150, 
    stats={"damage": 1, "speed": 10, "cooldown": 300, "energy_cost": 1, "color": (255, 0, 0), "size": (5, 10)}
)

WEAPON_RAPID_LASER = Module(
    "Rapid Laser", 
    "Faster firing laser with less damage per shot.",
    value=300, 
    stats={"damage": 0.5, "speed": 12, "cooldown": 150, "energy_cost": 1, "color": (0, 255, 0), "size": (3, 8)}
)

WEAPON_HEAVY_LASER = Module(
    "Heavy Laser", 
    "Powerful laser with slow firing rate.",
    value=400, 
    stats={"damage": 3, "speed": 8, "cooldown": 500, "energy_cost": 3, "color": (0, 0, 255), "size": (8, 15)}
)

# Scanner modules
SCANNER_BASIC = Module(
    "Basic Scanner", 
    "Standard scanner with limited range.",
    value=100, 
    stats={"range": 200, "accuracy": 0.7}
)

SCANNER_LONG_RANGE = Module(
    "Long Range Scanner", 
    "Extended range scanner with moderate accuracy.",
    value=250, 
    stats={"range": 350, "accuracy": 0.6}
)

SCANNER_PRECISION = Module(
    "Precision Scanner", 
    "High accuracy scanner with standard range.",
    value=300, 
    stats={"range": 180, "accuracy": 0.95}
)

# Facility modules
FACILITY_BASIC = Module(
    "Basic Facility", 
    "Standard ship facility with moderate capacity.",
    value=200, 
    stats={"capacity": 10, "efficiency": 0.7}
)

FACILITY_EXPANDED = Module(
    "Expanded Facility", 
    "Larger facility with more capacity.",
    value=400, 
    stats={"capacity": 20, "efficiency": 0.6}
)

FACILITY_EFFICIENT = Module(
    "Efficient Facility", 
    "Higher efficiency facility with standard capacity.",
    value=350, 
    stats={"capacity": 8, "efficiency": 0.9}
)

# Jump Engine modules
JUMP_ENGINE_BASIC = Module(
    "Basic Jump Engine", 
    "Standard jump engine with moderate range and cooldown.",
    value=500, 
    stats={"range": 1, "cooldown": 60, "energy_usage": 50}
)

JUMP_ENGINE_EXTENDED = Module(
    "Extended Jump Engine", 
    "Longer range jump engine with higher energy cost.",
    value=1000, 
    stats={"range": 2, "cooldown": 90, "energy_usage": 80}
)

JUMP_ENGINE_EFFICIENT = Module(
    "Efficient Jump Engine", 
    "Energy efficient jump engine with faster cooldown.",
    value=800, 
    stats={"range": 1, "cooldown": 40, "energy_usage": 40}
)

# Hangar modules
HANGAR_BASIC = Module(
    "Basic Hangar", 
    "Standard hangar with moderate drone capacity.",
    value=300, 
    stats={"capacity": 4, "recharge_rate": 1.0, "energy_output": 1.0}
)

HANGAR_EXPANDED = Module(
    "Expanded Hangar", 
    "Larger hangar with more drone capacity.",
    value=600, 
    stats={"capacity": 8, "recharge_rate": 0.8, "energy_output": 1.5}
)

HANGAR_EFFICIENT = Module(
    "Efficient Hangar", 
    "Energy efficient hangar with faster drone recharging.",
    value=500, 
    stats={"capacity": 3, "recharge_rate": 1.5, "energy_output": 2.0}
)

# Auxiliary modules
AUX_ENERGY_CELL = Module(
    "Energy Cell", 
    "Additional energy storage for ship systems.",
    value=200, 
    stats={"energy_capacity": 50, "recharge_boost": 0.2}
)

AUX_CARGO_BAY = Module(
    "Cargo Bay", 
    "Additional cargo storage.",
    value=250, 
    stats={"cargo_slots": 10}
)

AUX_REPAIR_UNIT = Module(
    "Repair Unit", 
    "Slowly repairs ship hull damage over time.",
    value=350, 
    stats={"repair_rate": 0.5, "energy_usage": 0.5}
)

AUX_SHIELD_BOOSTER = Module(
    "Shield Booster", 
    "Enhances shield regeneration.",
    value=300, 
    stats={"shield_boost": 0.3, "energy_usage": 0.3}
)

AUX_MINING_BEAM = Module(
    "Mining Beam", 
    "Secondary weapon that does extra damage to asteroids.",
    value=400, 
    stats={"mining_bonus": 1.5, "energy_usage": 1.2}
)

# Module collections by type
ENGINE_MODULES = [ENGINE_BASIC, ENGINE_SPEEDY, ENGINE_AGILE]
SHIELD_MODULES = [SHIELD_BASIC, SHIELD_REINFORCED, SHIELD_QUICK]
WEAPON_MODULES = [WEAPON_BASIC_LASER, WEAPON_RAPID_LASER, WEAPON_HEAVY_LASER]
SCANNER_MODULES = [SCANNER_BASIC, SCANNER_LONG_RANGE, SCANNER_PRECISION]
FACILITY_MODULES = [FACILITY_BASIC, FACILITY_EXPANDED, FACILITY_EFFICIENT]
JUMP_ENGINE_MODULES = [JUMP_ENGINE_BASIC, JUMP_ENGINE_EXTENDED, JUMP_ENGINE_EFFICIENT]
HANGAR_MODULES = [HANGAR_BASIC, HANGAR_EXPANDED, HANGAR_EFFICIENT]
AUX_MODULES = [AUX_ENERGY_CELL, AUX_CARGO_BAY, AUX_REPAIR_UNIT, AUX_SHIELD_BOOSTER, AUX_MINING_BEAM]