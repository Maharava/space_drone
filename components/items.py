import pygame
from game_config import *
from utils import load_image

class Item:
    """Base class for all items in the game"""
    def __init__(self, name, description, max_stack=20, value=1):
        self.name = name
        self.description = description
        self.max_stack = max_stack
        self.value = value
        self.image = None
    
    def get_image(self, size=40):
        """Get the item image at the specified size"""
        if not self.image or self.image.get_width() != size:
            self.image = load_image(self.name, size=size)
        return self.image

# Define ore items
class OreItem(Item):
    """Base class for ore items"""
    def __init__(self, name, description, color, max_stack=20, value=1):
        super().__init__(name, description, max_stack, value)
        self.color = color
    
    def get_image(self, size=40):
        """Get ore image with specific color"""
        if not self.image or self.image.get_width() != size:
            self.image = load_image(self.name, size=size, 
                                  fallback_color=self.color, is_circle=True)
        return self.image

# Define specific ore types
LOW_GRADE_ORE = OreItem(
    "Low-grade Ore", 
    "Common ore with minimal value. Found in most asteroids.",
    BROWN,
    max_stack=50,
    value=1
)

HIGH_GRADE_ORE = OreItem(
    "High-grade Ore",
    "Better quality ore with higher mineral content.",
    YELLOW,
    max_stack=30,
    value=3
)

RARE_ORE = OreItem(
    "Rare Ore",
    "Exotic minerals with unusual properties. Valuable for research.",
    PURPLE,
    max_stack=20,
    value=8
)

RAW_SILVER = OreItem(
    "Raw Silver",
    "Unrefined silver ore. Can be processed into currency.",
    SILVER,
    max_stack=20,
    value=5
)

# Define in one place
ORE_TYPES = {
    "low-grade": LOW_GRADE_ORE,
    "high-grade": HIGH_GRADE_ORE,
    "rare-ore": RARE_ORE,
    "silver": RAW_SILVER
}

# Equipment items
BASIC_SCANNER = Item(
    "Basic Scanner",
    "Simple scanner that helps detect asteroid composition.",
    max_stack=1,
    value=50
)

MINING_LASER_UPGRADE = Item(
    "Mining Laser Upgrade",
    "Increases mining laser efficiency by 15%.",
    max_stack=1,
    value=100
)

SHIELD_BOOSTER = Item(
    "Shield Booster",
    "Enhances shield capacity by 20 points.",
    max_stack=1,
    value=75
)

CARGO_EXPANDER = Item(
    "Cargo Expander",
    "Increases cargo capacity by 10 slots.",
    max_stack=1,
    value=120
)

# Resource items
BASIC_METAL = Item(
    "Basic Metal",
    "Common metal extracted from ore processing.",
    max_stack=50,
    value=2
)

ALLOY = Item(
    "Alloy",
    "Refined metal alloy used in ship and drone construction.",
    max_stack=30,
    value=10
)

ELECTRONICS = Item(
    "Electronics",
    "Electronic components for advanced modules.",
    max_stack=20,
    value=15
)

# Define merchant items once
MERCHANT_ITEMS = [
    BASIC_SCANNER,
    MINING_LASER_UPGRADE,
    SHIELD_BOOSTER,
    CARGO_EXPANDER
]