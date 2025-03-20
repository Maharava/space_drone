from game_config import *
from components.map.map_loader import MapLoader
from components.map.spawn_manager import SpawnManager
from components.map.area_state import AreaState

class MapSystem:
    """Main map system that coordinates map loading, spawning, and state tracking"""
    def __init__(self, all_sprites, asteroids):
        self.map_loader = MapLoader()
        self.spawn_manager = SpawnManager(all_sprites, asteroids)
        
        self.current_area_id = None
        self.previous_area_id = None
        self.jump_direction = None
        
        # Store area states
        self.area_states = {}
        
        # Import areas from loader for backward compatibility
        self.areas = self.map_loader.areas
    
    def change_area(self, area_id, direction=None):
        """Change to a different area"""
        if area_id not in self.map_loader.areas:
            print(f"Area '{area_id}' not found!")
            return False, None
        
        # Save current area state if we have one
        if self.current_area_id:
            self.save_area_state(self.current_area_id)
        
        # Store previous area for back-jumps
        self.previous_area_id = self.current_area_id
        self.current_area_id = area_id
        self.jump_direction = direction
        
        # Load the new area
        self.load_area(area_id)
        
        # Return success and jump direction
        return True, direction
    
    def load_area(self, area_id):
        """Load an area by ID"""
        # Check if we've already visited this area
        if area_id in self.area_states:
            # Restore the area's saved state
            self.area_states[area_id].restore()
            return True
            
        # Get area data
        area_data = self.map_loader.get_area(area_id)
        if not area_data:
            return False
        
        # Clear existing objects
        self.spawn_manager.clear_objects()
        
        # Spawn objects defined in area data
        if "objects" in area_data and area_data["objects"]:
            self.spawn_manager.spawn_objects(area_data["objects"])
        # Generate random objects if needed
        elif area_data["type"] == "asteroid_field":
            self.spawn_manager.generate_random_asteroids(30)
        
        # Create a new area state
        self.area_states[area_id] = AreaState(area_id, self.spawn_manager)
        
        return True
    
    def save_area_state(self, area_id):
        """Save the state of a specific area"""
        if area_id not in self.area_states:
            self.area_states[area_id] = AreaState(area_id, self.spawn_manager)
            
        self.area_states[area_id].save()
        return True
    
    def restore_area_state(self, area_id):
        """Restore a specific area to its saved state"""
        if area_id not in self.area_states:
            return False
            
        return self.area_states[area_id].restore()
    
    def get_connection(self, direction):
        """Get the ID of the connected area in the specified direction"""
        if not self.current_area_id:
            return None
            
        return self.map_loader.get_connection(self.current_area_id, direction)
    
    def can_jump(self, player_position):
        """Check if player is near an edge and can jump"""
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
        """Jump back to the previous area"""
        if self.previous_area_id:
            return self.change_area(self.previous_area_id)
        return False, None
    
    def get_opposite_direction(self, direction):
        """Get the opposite direction"""
        opposites = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        return opposites.get(direction)
    
    def get_nearest_station(self, player_position):
        """Find the nearest space station to the player"""
        return self.spawn_manager.get_nearest_station(player_position)