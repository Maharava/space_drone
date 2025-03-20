import pygame
import json
import os
import random
from game_config import *
from components.asteroid import Asteroid

class Area:
    def __init__(self, area_data, all_sprites, asteroids):
        self.id = area_data["id"]
        self.name = area_data["name"]
        self.type = area_data["type"]
        self.connections = area_data["connections"]
        self.all_sprites = all_sprites
        self.asteroids = asteroids
        
        # Clear existing asteroids and load new ones
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

class MapSystem:
    def __init__(self, all_sprites, asteroids):
        self.areas = {}
        self.current_area_id = None
        self.previous_area_id = None
        self.all_sprites = all_sprites
        self.asteroids = asteroids
        
        # Load map data
        self.load_areas()
    
    def load_areas(self):
        if not os.path.exists("maps"):
            print("Maps directory not found at:", os.path.abspath("maps"))
            return
        
        map_files = [f for f in os.listdir("maps") if f.endswith(".json")]
        print(f"Found {len(map_files)} map file(s) in {os.path.abspath('maps')}")
        
        for filename in map_files:
            try:
                with open(os.path.join("maps", filename), "r") as f:
                    area_data = json.load(f)
                    self.areas[area_data["id"]] = area_data
                    print(f"Loaded area: {area_data['id']}")
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
    
    def change_area(self, area_id):
        if area_id not in self.areas:
            print(f"Area '{area_id}' not found! Available areas: {list(self.areas.keys())}")
            return False
        
        # Store previous area for back-jumps
        self.previous_area_id = self.current_area_id
        self.current_area_id = area_id
        
        # Load the new area
        area_data = self.areas[area_id]
        new_area = Area(area_data, self.all_sprites, self.asteroids)
        print(f"Jumped to {new_area.name}")
        return True
    
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
        return False