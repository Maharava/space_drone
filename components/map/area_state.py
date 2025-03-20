class AreaState:
    """Component for tracking and saving area states"""
    def __init__(self, area_id, spawn_manager):
        self.area_id = area_id
        self.spawn_manager = spawn_manager
        self.saved_state = None
    
    def save(self):
        """Save the current state of the area"""
        self.saved_state = {
            "asteroids": [],
            "stations": []
        }
        
        # Save asteroid positions, types and health
        for asteroid in self.spawn_manager.asteroids:
            self.saved_state["asteroids"].append({
                "position": (asteroid.position.x, asteroid.position.y),
                "type": asteroid.asteroid_type,
                "health": asteroid.health
            })
        
        # Save station data
        for station in self.spawn_manager.stations:
            self.saved_state["stations"].append({
                "position": (station.position.x, station.position.y),
                "name": station.name,
                "dialog": station.dialog
            })
    
    def restore(self):
        """Restore the area to its saved state"""
        if not self.saved_state:
            return False
        
        # Clear existing objects
        self.spawn_manager.clear_objects()
        
        # Restore asteroids
        if "asteroids" in self.saved_state:
            for asteroid_data in self.saved_state["asteroids"]:
                # Create asteroid with saved data
                asteroid = self.spawn_manager.spawn_asteroid({
                    "type": "asteroid",
                    "x": asteroid_data["position"][0],
                    "y": asteroid_data["position"][1],
                    "asteroid_type": asteroid_data["type"]
                })
                
                # Set health
                if asteroid:
                    asteroid.health = asteroid_data["health"]
        
        # Restore stations
        if "stations" in self.saved_state:
            for station_data in self.saved_state["stations"]:
                self.spawn_manager.spawn_station({
                    "type": "station",
                    "x": station_data["position"][0],
                    "y": station_data["position"][1],
                    "name": station_data["name"],
                    "dialog": station_data["dialog"]
                })
                
        return True