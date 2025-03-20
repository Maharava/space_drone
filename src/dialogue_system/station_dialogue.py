from .dialogue import DialogueSystem
from .flags import FlagSystem
from .npc import NPC

class StationDialogueHandler:
    """
    Handles dialogue for space stations.
    Designed to be composed with existing SpaceStation class rather than inheriting.
    """
    def __init__(self, station_name, dialogue_id=None, flags_system=None):
        self.station_name = station_name
        self.dialogue_id = dialogue_id
        self.flags = flags_system or FlagSystem()
        self.npcs = {}
        
        # If the station has its own dialogue
        if dialogue_id:
            self.dialogue_system = DialogueSystem(flags_system=self.flags)
    
    def add_npc(self, npc_name, npc_dialogue_id):
        """Add an NPC to the station"""
        self.npcs[npc_name] = NPC(npc_name, npc_dialogue_id, self.flags)
        return self.npcs[npc_name]
    
    def get_npc(self, npc_name):
        """Get an NPC by name"""
        return self.npcs.get(npc_name)
    
    def get_npc_list(self):
        """Get list of available NPCs"""
        return list(self.npcs.keys())
    
    def start_station_dialogue(self):
        """Start dialogue with the station itself"""
        if not self.dialogue_id:
            return False
            
        success = self.dialogue_system.load_dialogue(self.dialogue_id)
        if not success:
            print(f"Could not start dialogue with {self.station_name}")
            return False
        return True
    
    def get_current_text(self):
        """Get the current dialogue text"""
        if not hasattr(self, 'dialogue_system') or not self.dialogue_system.current_node:
            return None
        return self.dialogue_system.get_current_node_text()
    
    def get_dialogue_options(self):
        """Get available dialogue options"""
        if not hasattr(self, 'dialogue_system') or not self.dialogue_system.current_node:
            return []
        return self.dialogue_system.get_available_options()
    
    def select_option(self, option_index):
        """Select a dialogue option"""
        if not hasattr(self, 'dialogue_system') or not self.dialogue_system.current_node:
            return False
        return self.dialogue_system.select_option(option_index)