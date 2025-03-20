import pygame
from game_config import *

class SpaceStation(pygame.sprite.Sprite):
    def __init__(self, station_data=None):
        super().__init__()
        
        # Set default values
        self.position = pygame.math.Vector2(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)
        self.name = "Space Station"
        self.dialog = "Welcome to the station, traveler."
        self.station_size = 120  # Default size
        
        # Override with station data if provided
        if station_data:
            if "x" in station_data and "y" in station_data:
                self.position = pygame.math.Vector2(station_data["x"], station_data["y"])
            if "name" in station_data:
                self.name = station_data["name"]
            if "dialog" in station_data:
                self.dialog = station_data["dialog"]
            if "size" in station_data:
                self.station_size = station_data["size"]
        
        # Create station image
        try:
            self.image = pygame.image.load("assets/station.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (self.station_size, self.station_size))
        except:
            # Create diamond if image not found
            self.image = pygame.Surface((self.station_size, self.station_size), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, SILVER, [
                (self.station_size // 2, 0),  # Top
                (self.station_size, self.station_size // 2),  # Right
                (self.station_size // 2, self.station_size),  # Bottom
                (0, self.station_size // 2)  # Left
            ])
            # Add some details
            pygame.draw.polygon(self.image, DARK_GREY, [
                (self.station_size // 2, self.station_size // 4),  # Top inner
                (self.station_size * 3 // 4, self.station_size // 2),  # Right inner
                (self.station_size // 2, self.station_size * 3 // 4),  # Bottom inner
                (self.station_size // 4, self.station_size // 2)  # Left inner
            ])
        
        self.rect = self.image.get_rect(center=self.position)
        self.interaction_radius = self.station_size * 1.5  # Area where player can interact
    
    def update(self, game_state):
        # Stations don't move, but we need this for the sprite group
        pass
    
    def can_interact(self, player_position):
        """Check if player is close enough to interact"""
        distance = pygame.math.Vector2(self.rect.center).distance_to(player_position)
        return distance <= self.interaction_radius