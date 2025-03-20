from .npc import NPC
from .flags import FlagSystem
from .quests import QuestSystem

class NPCInteraction:
    def __init__(self):
        self.flags = FlagSystem()
        self.quest_system = QuestSystem(flags_system=self.flags)
        self.current_npc = None
    
    def interact_with_npc(self, npc_name, dialogue_id):
        """Start interaction with an NPC"""
        self.current_npc = NPC(npc_name, dialogue_id, self.flags)
        if self.current_npc.start_conversation():
            return self._display_current_dialogue()
        return False
    
    def _display_current_dialogue(self):
        """Display the current dialogue node"""
        if not self.current_npc:
            return False
            
        # Get NPC text
        npc_text = self.current_npc.get_current_text()
        if not npc_text:
            self.current_npc = None
            return False
            
        # Display NPC text
        print(f"{self.current_npc.name}: {npc_text}")
        
        # Get and display options
        options = self.current_npc.get_dialogue_options()
        for option in options:
            print(f"{option['index'] + 1}. {option['text']}")
            
        return True
    
    def select_dialogue_option(self, option_index):
        """Select a dialogue option (adjusted for 1-based indexing for users)"""
        if not self.current_npc:
            return False
            
        # Convert to 0-based for internal use
        internal_index = option_index - 1
        
        # Select the option
        result = self.current_npc.select_option(internal_index)
        
        # If dialogue ended, clear current NPC
        if not result or not self.current_npc.dialogue_system.current_node:
            self.current_npc = None
            return False
            
        # Display next dialogue
        return self._display_current_dialogue()