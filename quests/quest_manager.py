"""
Quest manager for the game, handling dialogue and quest systems.
"""

import os
from components.dialogue_system.flags import FlagSystem
from components.dialogue_system.quests import QuestSystem
from components.dialogue_system.integration import add_dialogue_to_station

class QuestManager:
    """Manages quests and dialogue for the game."""
    def __init__(self, game):
        """Initialize the quest manager."""
        self.game = game
        
        # Create directories if they don't exist
        os.makedirs("flags", exist_ok=True)
        
        # Initialize flag and quest systems
        self.flags = FlagSystem("flags/game_flags.json")
        self.quest_system = QuestSystem("quests", self.flags)
        
        # Load the mining quest
        self.quest_system.start_quest("mining_quest")
        
        # Track active dialogue
        self.current_station = None
        self.current_npc = None
        self.current_dialogue = None
        
        print("Quest manager initialized")
    
    def add_dialogue_to_station(self, station):
        """Add dialogue to a station based on its name."""
        if station.name == "Copernicus Station":
            # Add station dialogue
            dialogue_handler = add_dialogue_to_station(station, "copernicus_station", self.flags)
            
            # Add Mining Foreman NPC
            dialogue_handler.add_npc("Mining Foreman", "mining_foreman_dialogue")
            
            print(f"Added dialogue to {station.name}")
            return dialogue_handler
        
        return None
    
    def start_station_dialogue(self, station):
        """Start dialogue with a station."""
        if not hasattr(station, '_dialogue_handler'):
            return False
        
        self.current_station = station
        self.current_npc = None
        
        # Start station dialogue
        result = station._dialogue_handler.start_station_dialogue()
        if result:
            self.current_dialogue = station._dialogue_handler
            return True
        
        return False
    
    def start_direct_npc_dialogue(self, npc_name):
        """Start dialogue with a specific NPC - handles state setup"""
        # Find the current station
        station = self.game.map_system.get_nearest_station(self.game.player.position)
        if not station:
            print("No station nearby")
            return False
            
        # Make sure station has dialogue
        if not hasattr(station, '_dialogue_handler'):
            dialogue_handler = self.add_dialogue_to_station(station)
            if not dialogue_handler:
                print(f"Could not add dialogue to {station.name}")
                return False
        
        # Get the NPC
        npc = station._dialogue_handler.get_npc(npc_name)
        if not npc:
            print(f"NPC '{npc_name}' not found")
            return False
        
        # Set current state and start dialogue
        self.current_station = station
        self.current_dialogue = station._dialogue_handler
        
        # Make sure we save any pending flag changes before starting dialogue
        self.flags.save_flags()
        
        # Start NPC dialogue
        if npc.start_conversation():
            self.current_npc = npc
            return True
            
        return False
    
    def get_current_text(self):
        """Get the current dialogue text."""
        if not self.current_dialogue:
            return None
        
        if self.current_npc:
            return self.current_npc.get_current_text()
        
        return self.current_dialogue.get_current_text()
    
    def get_current_options(self):
        """Get available dialogue options."""
        if not self.current_dialogue:
            return []
        
        if self.current_npc:
            return self.current_npc.get_dialogue_options()
        
        return self.current_dialogue.get_dialogue_options()
    
    def select_option(self, option_index):
        """Select a dialogue option."""
        if not self.current_dialogue:
            return False
        
        if self.current_npc:
            result = self.current_npc.select_option(option_index)
            
            # Check if dialogue ended
            if not result:
                self.current_npc = None
                
            # Check for quest completion
            if self.flags.get_flag("MiningQuestCompleted", False):
                # Add reward to player
                self.game.player.stats.silver += 50
                print("Mining quest completed! Rewarded 50 silver.")
                # Make sure we save this completion state
                self.flags.save_flags()
                
            return result
        
        # Handle station dialogue
        options = self.current_dialogue.get_dialogue_options()
        if option_index >= len(options):
            return False
        
        option = options[option_index]
        option_text = option.get('text', '').lower()
        
        # Check if this is about the Mining Foreman
        if ("mining" in option_text and "foreman" in option_text) or "foreman" in option_text:
            # First select the option to progress dialogue
            self.current_dialogue.select_option(option_index)
            
            # Then try to start Mining Foreman dialogue
            if self.start_direct_npc_dialogue("Mining Foreman"):
                return True
            
            return False
        
        # Standard option selection
        result = self.current_dialogue.select_option(option_index)
        
        # Check if dialogue ended
        if not result:
            self.current_dialogue = None
            
        return result
    
    def update_quest_progress(self, item):
        """Update quest progress when an item is collected."""
        if item.name == "Rare Ore":
            # Check if quest is active
            if self.flags.get_flag("MiningQuestAccepted", False) and not self.flags.get_flag("MiningQuestCompleted", False):
                # Get current count
                current_count = self.flags.get_flag("OreCollected", 0)
                # Increment count
                self.flags.set_flag("OreCollected", current_count + 1)
                print(f"Mining quest progress: {current_count + 1}/5 Rare Ore collected")
                
                # Only save periodically to avoid lag
                if (current_count + 1) % 5 == 0 or (current_count + 1) >= 5:
                    self.flags.save_flags()
                    
                return True
        
        return False