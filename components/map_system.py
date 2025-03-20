import pygame
import json
import os
import random
from game_config import *
from components.asteroid import Asteroid
from components.space_station import SpaceStation

class Area:
    def __init__(self, area_data, all_sprites, asteroids):
        self.id = area_data["id"]
        self.name = area_data["name"]
        self.type = area_data["type"]
        self.connections = area_data["connections"]
        self.all_sprites = all_sprites
        self.asteroids = asteroids
        self.stations = pygame.sprite.Group()
        self.saved_state = {}
        
        # Clear existing asteroids
        for sprite in list(self.asteroids):
            sprite.kill()
            
        # Load objects defined in area data
        if "objects" in area_data and area_data["objects"]:
            for obj in area_data["objects"]:
                if obj["type"] == "asteroid":
                    self.spawn_asteroid(obj)
        # Generate random objects if needed
        elif self.type == "asteroid_field":
            self.generate_random_asteroids()
            
        # Add space station if needed
        if self.id == "copernicus-outer-orbit":
            self.add_space_station()
    
    def spawn_asteroid(self, data):
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
        
        self.all_sprites.add(asteroid)
        self.asteroids.add(asteroid)
    
    def generate_random_asteroids(self):
        for _ in range(30):
            # Random asteroid type distribution
            roll = random.random()
            if roll < 0.5:
                asteroid_type = "regular"
            elif roll < 0.8:
                asteroid_type = "dry"
            else:
                asteroid_type = "rich"
                
            asteroid = Asteroid(asteroid_type=asteroid_type)
            self.all_sprites.add(asteroid)
            self.asteroids.add(asteroid)
    
    def add_space_station(self):
        # Add a space station in the middle of the area
        station = SpaceStation(position=(WORLD_WIDTH // 2, WORLD_HEIGHT // 2))
        self.all_sprites.add(station)
        self.stations.add(station)
    
    def save_state(self):
        """Save the current state of this area"""
        self.saved_state = {
            "asteroids": []
        }
        
        # Save asteroid positions, types and health
        for asteroid in self.asteroids:
            self.saved_state["asteroids"].append({
                "position": (asteroid.position.x, asteroid.position.y),
                "type": asteroid.asteroid_type,
                "health": asteroid.health
            })
    
    def restore_state(self):
        """Restore the area to its saved state"""
        if not self.saved_state:
            return
            
        # Clear existing asteroids
        for sprite in list(self.asteroids):
            sprite.kill()
        
        # Restore asteroids
        if "asteroids" in self.saved_state:
            for asteroid_data in self.saved_state["asteroids"]:
                asteroid = Asteroid(asteroid_type=asteroid_data["type"])
                asteroid.position = pygame.math.Vector2(asteroid_data["position"])
                asteroid.rect.center = asteroid_data["position"]
                asteroid.health = asteroid_data["health"]
                
                self.all_sprites.add(asteroid)
                self.asteroids.add(asteroid)

class MapSystem:
    def __init__(self, all_sprites, asteroids):
        self.areas = {}
        self.current_area_id = None
        self.previous_area_id = None
        self.jump_direction = None
        self.all_sprites = all_sprites
        self.asteroids = asteroids
        self.saved_areas = {}
        
        # Load map data
        self.load_areas()
    
    def load_areas(self):
        if not os.path.exists("maps"):
            print("Maps directory not found. Creating directory...")
            try:
                os.makedirs("maps")
            except:
                print("Failed to create maps directory")
            return False
        
        map_files = [f for f in os.listdir("maps") if f.endswith(".json")]
        if not map_files:
            print("No map files found")
            return False
            
        success = False
        for filename in map_files:
            try:
                with open(os.path.join("maps", filename), "r") as f:
                    area_data = json.load(f)
                    self.areas[area_data["id"]] = area_data
                    success = True
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
        
        return success
    
    def change_area(self, area_id, direction=None):
        if area_id not in self.areas:
            print(f"Area '{area_id}' not found!")
            return False, None
        
        # Save current area state if we have one
        if self.current_area_id and self.current_area_id in self.saved_areas:
            self.saved_areas[self.current_area_id].save_state()
        
        # Store previous area for back-jumps
        self.previous_area_id = self.current_area_id
        self.current_area_id = area_id
        self.jump_direction = direction
        
        # Check if we've already visited this area
        if area_id in self.saved_areas:
            # Restore the area's saved state
            self.saved_areas[area_id].restore_state()
            return True, direction
        else:
            # Load the new area
            area_data = self.areas[area_id]
            new_area = Area(area_data, self.all_sprites, self.asteroids)
            self.saved_areas[area_id] = new_area
        
        # Return success and jump direction
        return True, direction
    
    def get_connection(self, direction):
        if not self.current_area_id:
            return None
            
        area_data = self.areas[self.current_area_id]
        return area_data["connections"].get(direction)
    
    def can_jump(self, player_position):
        margin = 50
        
        if player_position.x < margin:
            return "west"
        elif player_position.x > WORLD_WIDTH - margin:
            return "east"
        elif player_position.y < margin:
            return "north"
        elif player_position.y > WORLD_HEIGHT - margin:
            return "south"
        
        return None
    
    def jump_back(self):
        if self.previous_area_id:
            return self.change_area(self.previous_area_id)
        return False, None
    
    def get_opposite_direction(self, direction):
        if direction == "north":
            return "south"
        elif direction == "south":
            return "north"
        elif direction == "east":
            return "west"
        elif direction == "west":
            return "east"
        return None
    
    def get_nearest_station(self, player_position):
        """Find the nearest space station to the player"""
        if not self.current_area_id or self.current_area_id not in self.saved_areas:
            return None
            
        current_area = self.saved_areas[self.current_area_id]
        
        nearest_station = None
        min_distance = float('inf')
        
        for station in current_area.stations:
            dist = pygame.math.Vector2(station.rect.center).distance_to(player_position)
            if dist < min_distance:
                min_distance = dist
                nearest_station = station
        
        return nearest_station
    
    def save_area_state(self, area_id):
        """Save the state of a specific area"""
        if area_id not in self.saved_areas:
            return False
            
        area = self.saved_areas[area_id]
        area.save_state()
        return True
    
    def restore_area_state(self, area_id):
        """Restore a specific area to its saved state"""
        if area_id not in self.saved_areas:
            return False
            
        area = self.saved_areas[area_id]
        area.restore_state()
        return True