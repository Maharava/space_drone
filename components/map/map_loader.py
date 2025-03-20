import os
import json

class MapLoader:
    """Component for loading and providing map data"""
    def __init__(self, maps_dir="maps"):
        self.maps_dir = maps_dir
        self.areas = {}
        self.load_all_maps()
    
    def load_all_maps(self):
        """Load all map data from the maps directory"""
        # Create maps directory if it doesn't exist
        if not os.path.exists(self.maps_dir):
            print("Maps directory not found. Creating directory...")
            try:
                os.makedirs(self.maps_dir)
            except:
                print("Failed to create maps directory")
            return False
        
        # Get all JSON files in the maps directory
        map_files = [f for f in os.listdir(self.maps_dir) if f.endswith(".json")]
        if not map_files:
            print("No map files found")
            return False
        
        # Load each map file
        success = False
        for filename in map_files:
            try:
                with open(os.path.join(self.maps_dir, filename), "r") as f:
                    area_data = json.load(f)
                    self.areas[area_data["id"]] = area_data
                    success = True
            except Exception as e:
                print(f"Error loading {filename}: {str(e)}")
        
        print(f"Loaded {len(self.areas)} map areas")
        return success
    
    def get_area(self, area_id):
        """Get area data by ID"""
        if area_id in self.areas:
            return self.areas[area_id]
        return None
    
    def get_connection(self, area_id, direction):
        """Get the ID of the connected area in the specified direction"""
        if area_id not in self.areas:
            return None
        
        area = self.areas[area_id]
        return area["connections"].get(direction)
    
    def get_area_name(self, area_id):
        """Get the name of an area by ID"""
        if area_id in self.areas:
            return self.areas[area_id].get("name", area_id)
        return "Unknown Area"
    
    def get_area_type(self, area_id):
        """Get the type of an area by ID"""
        if area_id in self.areas:
            return self.areas[area_id].get("type", "empty")
        return "empty"
    
    def get_area_objects(self, area_id):
        """Get the objects in an area by ID"""
        if area_id in self.areas:
            return self.areas[area_id].get("objects", [])
        return []