import pygame
from game_config import *

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
        if not self.image:
            self.load_image()
        
        return pygame.transform.scale(self.image, (size, size))
    
    def load_image(self, size=40):
        """Load the item image or create a fallback"""
        try:
            self.image = pygame.image.load(f"assets/{self.name.lower().replace(' ', '_')}.png").convert_alpha()
        except:
            # Create a placeholder image
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, GREY, (size // 2, size // 2), size // 2)
            font = pygame.font.SysFont(None, 20)
            text = font.render(self.name[0], True, WHITE)
            self.image.blit(text, (size // 2 - text.get_width() // 2, 
                                  size // 2 - text.get_height() // 2))

# Define ore items
class OreItem(Item):
    """Base class for ore items"""
    def __init__(self, name, description, color, max_stack=20, value=1):
        super().__init__(name, description, max_stack, value)
        self.color = color
    
    def load_image(self, size=40):
        """Load ore image or create a colored circle"""
        try:
            self.image = pygame.image.load(f"assets/{self.name.lower().replace(' ', '_')}.png").convert_alpha()
        except:
            # Create a colored ore circle
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.color, (size // 2, size // 2), size // 2)

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

# Dictionary to map old ore types to new item objects
ORE_TYPES = {
    "low-grade": LOW_GRADE_ORE,
    "high-grade": HIGH_GRADE_ORE,
    "rare-ore": RARE_ORE,
    "silver": RAW_SILVER
}

# Some basic equipment items for the merchant
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

# List of items available for purchase from merchants
MERCHANT_ITEMS = [
    BASIC_SCANNER,
    MINING_LASER_UPGRADE,
    SHIELD_BOOSTER,
    CARGO_EXPANDER
]

ORE_TYPES = {
    "low-grade": LOW_GRADE_ORE,
    "high-grade": HIGH_GRADE_ORE,
    "rare-ore": RARE_ORE,
    "silver": RAW_SILVER,
    "Raw Silver": RAW_SILVER  # Add this for consistency
}

# Some basic equipment items for the merchant
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

# New resource items
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

# List of items available for purchase from merchants
MERCHANT_ITEMS = [
    BASIC_SCANNER,
    MINING_LASER_UPGRADE,
    SHIELD_BOOSTER,
    CARGO_EXPANDER
]