"""Quest manager for the game, handling dialogue and quest systems."""

import os
import json
from components.dialogue_system.flags import FlagSystem
from components.dialogue_system.npc import NPC

class QuestManager:
    """Manages quests and dialogue for the game."""
    def __init__(self, game):
        self.game = game
        
        # Initialize flag system
        os.makedirs("flags", exist_ok=True)
        self.flags = FlagSystem("flags/game_flags.json")
        
        # Initialize default quest state if needed
        if not os.path.exists("flags/game_flags.json"):
            self.init_default_quest_states()
        
        # Active dialogue tracking
        self.current_station = None
        self.current_npc = None
        
        print("Quest manager initialized with flags:", self.flags.flags)
    
    def init_default_quest_states(self):
        """Initialize default quest states."""
        default_flags = {
            "mining_quest": 0  # 0=not started, 1=in progress, 2=completed, 3=failed
        }
        self.flags.flags = default_flags
        self.flags.save_flags()
    
    def add_dialogue_to_station(self, station):
        """Add dialogue handlers to a station."""
        # Only handle Copernicus Station for now
        if station.name == "Copernicus Station":
            # Add Mining Foreman NPC
            station._dialogue_handler = {
                "npcs": {
                    "Mining Foreman": NPC("Mining Foreman", "mining_foreman_dialogue", self.flags, self.game)
                }
            }
            print(f"Added dialogue handlers to {station.name}")
            return station._dialogue_handler
        return None
    
    def start_station_dialogue(self, station):
        """Start dialogue with a station (basic placeholder)."""
        # Make sure station has dialogue handlers
        if not hasattr(station, '_dialogue_handler'):
            self.add_dialogue_to_station(station)
        
        # Check if dialogue was added
        if hasattr(station, '_dialogue_handler'):
            self.current_station = station
            self.current_npc = None
            return True
        
        return False
    
    def start_direct_npc_dialogue(self, npc_name):
        """Start dialogue with a specific NPC."""
        # Find nearest station
        station = self.game.map_system.get_nearest_station(self.game.player.position)
        if not station:
            print("No station nearby")
            return False
        
        # Add dialogue handlers if needed
        if not hasattr(station, '_dialogue_handler'):
            self.add_dialogue_to_station(station)
        
        # Get NPC
        if not hasattr(station, '_dialogue_handler') or npc_name not in station._dialogue_handler["npcs"]:
            print(f"NPC {npc_name} not found at station")
            return False
        
        npc = station._dialogue_handler["npcs"][npc_name]
        
        # Start conversation
        if npc.start_conversation():
            self.current_station = station
            self.current_npc = npc
            print(f"Started dialogue with {npc_name}")
            return True
        
        return False
    
    def get_current_text(self):
        """Get current dialogue text."""
        if self.current_npc:
            return self.current_npc.get_current_text()
        return "Welcome to the station."
    
    def get_current_options(self):
        """Get current dialogue options."""
        if self.current_npc:
            return self.current_npc.get_dialogue_options()
        
        # Default station options
        if self.current_station and self.current_station.name == "Copernicus Station":
            return [
                {
                    "text": "I'd like to speak with the Mining Foreman.",
                    "index": 0
                },
                {
                    "text": "Just passing through.",
                    "index": 1
                }
            ]
        
        return []
    
    def select_option(self, option_index):
        """Select dialogue option."""
        if self.current_npc:
            # Process NPC dialogue option
            result = self.current_npc.select_option(option_index)
            return result
        
        # Handle station dialogue options
        if self.current_station:
            # Handle Mining Foreman option for Copernicus Station
            if option_index == 0 and self.current_station.name == "Copernicus Station":
                return self.start_direct_npc_dialogue("Mining Foreman")
        
        return False
    
    def get_mining_quest_progress(self):
        """Get mining quest progress."""
        status = self.flags.get_flag("mining_quest", 0)
        if status == 0:
            return "Not Started"
        elif status == 1:
            # In progress - count rare ore
            ore_count = self.count_rare_ore()
            return f"In Progress ({ore_count}/5 ore)"
        elif status == 2:
            return "Completed"
        else:
            return "Failed"
    
    def count_rare_ore(self):
        """Count how much rare ore the player has."""
        try:
            rare_ore_count = 0
            
            # Check inventory for Rare Ore
            for row in self.game.player.inventory:
                for slot in row:
                    if slot["item"] and slot["item"].name == "Rare Ore":
                        rare_ore_count += slot["count"]
            
            return rare_ore_count
        except Exception as e:
            print(f"Error counting ore: {e}")
            return 0