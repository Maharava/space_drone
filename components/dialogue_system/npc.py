from .dialogue import DialogueSystem

class NPC:
    """Class representing an NPC with dialogue capabilities."""
    def __init__(self, name, dialogue_id, flags_system, game_ref=None):
        self.name = name
        self.dialogue_id = dialogue_id
        self.dialogue_system = DialogueSystem(flags_system, game_ref)
    
    def start_conversation(self):
        """Start conversation with this NPC."""
        success = self.dialogue_system.load_dialogue(self.dialogue_id)
        if not success:
            print(f"Could not start conversation with {self.name}")
            return False
        return True
    
    def get_current_text(self):
        """Get current dialogue text from NPC."""
        return self.dialogue_system.get_current_node_text()
    
    def get_dialogue_options(self):
        """Get available dialogue options."""
        return self.dialogue_system.get_available_options()
    
    def select_option(self, option_index):
        """Select a dialogue option."""
        return self.dialogue_system.select_option(option_index)