import pygame
import random
from game_config import *
from components.asteroid import Asteroid
from components.space_station import SpaceStation

class SpawnManager:
    """Component for spawning game objects in areas"""
    def __init__(self, all_sprites, asteroids, game=None):
        self.all_sprites = all_sprites
        self.asteroids = asteroids
        self.stations = pygame.sprite.Group()
        self.game = game  # Store reference to the main game
    
    def clear_objects(self):
        """Clear all objects from the area"""
        for sprite in list(self.asteroids):
            sprite.kill()
        
        for sprite in list(self.stations):
            sprite.kill()
    
    def spawn_objects(self, objects):
        """Spawn objects from area data"""
        if not objects:
            return
            
        for obj in objects:
            if obj["type"] == "asteroid":
                self.spawn_asteroid(obj)
            elif obj["type"] == "station":
                self.spawn_station(obj)
    
    def spawn_asteroid(self, data):
        """Spawn an asteroid from data"""
        asteroid_type = data.get("asteroid_type", "regular")
        asteroid = Asteroid(asteroid_type=asteroid_type)
        
        # Set position
        if "x" in data and "y" in data:
            asteroid.rect.center = (data["x"], data["y"])
            asteroid.position = pygame.math.Vector2(asteroid.rect.center)
        
        # Set size
        if "size" in data:
            asteroid.size = data["size"]
            asteroid.image = pygame.transform.scale(asteroid.image, (asteroid.size, asteroid.size))
            asteroid.rect = asteroid.image.get_rect(center=asteroid.position)
        
        # Add to sprite groups
        self.all_sprites.add(asteroid)
        self.asteroids.add(asteroid)
        
        return asteroid
    
    def spawn_station(self, data):
        """Spawn a space station from data"""
        station = SpaceStation(data)
        
        # Add to sprite groups
        self.all_sprites.add(station)
        self.stations.add(station)
        
        # Add dialogue if quest manager exists
        if hasattr(self.game, 'quest_manager'):
            self.game.quest_manager.add_dialogue_to_station(station)
        
        return station
    
    def generate_random_asteroids(self, count=30):
        """Generate random asteroids"""
        for _ in range(count):
            # Random asteroid type distribution
            roll = random.random()
            if roll < 0.5:
                asteroid_type = "regular"
            elif roll < 0.8:
                asteroid_type = "dry"
            else:
                asteroid_type = "rich"
                
            # Random position
            x = random.randint(50, WORLD_WIDTH - 50)
            y = random.randint(50, WORLD_HEIGHT - 50)
            
            # Random size
            size = random.choice([32, 48, 64, 80, 96])
            
            # Create asteroid data
            asteroid_data = {
                "type": "asteroid",
                "x": x,
                "y": y,
                "size": size,
                "asteroid_type": asteroid_type
            }
            
            # Spawn asteroid
            self.spawn_asteroid(asteroid_data)
    
    def get_nearest_station(self, position):
        """Find the nearest space station to the given position"""
        nearest_station = None
        min_distance = float('inf')
        
        for station in self.stations:
            dist = pygame.math.Vector2(station.rect.center).distance_to(position)
            if dist < min_distance:
                min_distance = dist
                nearest_station = station
        
        return nearest_station