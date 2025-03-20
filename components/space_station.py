import pygame
from game_config import *

class SpaceStation(pygame.sprite.Sprite):
    def __init__(self, position=(WORLD_WIDTH // 2, WORLD_HEIGHT // 2)):
        super().__init__()
        self.position = pygame.math.Vector2(position)
        
        # Create diamond shape for the station
        player_size = 30  # Assuming player ship is about 30 pixels
        station_size = player_size * 4
        
        try:
            self.image = pygame.image.load("assets/station.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (station_size, station_size))
        except:
            # Create diamond if image not found
            self.image = pygame.Surface((station_size, station_size), pygame.SRCALPHA)
            pygame.draw.polygon(self.image, SILVER, [
                (station_size // 2, 0),  # Top
                (station_size, station_size // 2),  # Right
                (station_size // 2, station_size),  # Bottom
                (0, station_size // 2)  # Left
            ])
            # Add some details
            pygame.draw.polygon(self.image, DARK_GREY, [
                (station_size // 2, station_size // 4),  # Top inner
                (station_size * 3 // 4, station_size // 2),  # Right inner
                (station_size // 2, station_size * 3 // 4),  # Bottom inner
                (station_size // 4, station_size // 2)  # Left inner
            ])
        
        self.rect = self.image.get_rect(center=position)
        self.interaction_radius = station_size * 1.5  # Area where player can interact
        
        # Station data
        self.name = "Copernicus Station"
        self.dialog = "Welcome to Copernicus Station, traveler. We have supplies and drones for miners like you. Feel free to dock and trade your ores for equipment."
    
    def update(self, game_state):
        # Stations don't move, but we need this for the sprite group
        pass
    
    def can_interact(self, player_position):
        """Check if player is close enough to interact"""
        distance = pygame.math.Vector2(self.rect.center).distance_to(player_position)
        return distance <= self.interaction_radius