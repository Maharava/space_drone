import json
import os
from .flags import FlagSystem

class DialogueSystem:
    def __init__(self, dialogue_folder="dialogue", flags_system=None):
        self.dialogue_folder = dialogue_folder
        self.flags = flags_system or FlagSystem()
        self.current_dialogue = None
        self.current_node = None
        
        # Create dialogue folder if it doesn't exist
        os.makedirs(dialogue_folder, exist_ok=True)
    
    def load_dialogue(self, dialogue_name):
        """Load a dialogue file"""
        file_path = os.path.join(self.dialogue_folder, f"{dialogue_name}.json")
        if not os.path.exists(file_path):
            print(f"Dialogue file not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                self.current_dialogue = json.load(f)
            
            # Determine the starting node based on flags
            self._determine_starting_node()
            return True
        except json.JSONDecodeError:
            print(f"Error parsing dialogue file: {file_path}")
            return False
    
    def _determine_starting_node(self):
        """Determine the starting node based on flags and state"""
        # Default to root
        self.current_node = "root"
        
        # Check for node override based on dialogue-specific flags
        if self.current_dialogue.get("node_conditions"):
            for node_name, conditions in self.current_dialogue["node_conditions"].items():
                all_conditions_met = True
                for flag, value in conditions.items():
                    if self.flags.get_flag(flag) != value:
                        all_conditions_met = False
                        break
                
                if all_conditions_met:
                    self.current_node = node_name
                    break
    
    def get_current_node_text(self):
        """Get the NPC text for the current node"""
        if not self.current_dialogue or not self.current_node:
            return None
            
        return self.current_dialogue.get(self.current_node, {}).get("npc_text", "")
    
    def get_available_options(self):
        """Get available player options for the current node"""
        if not self.current_dialogue or not self.current_node:
            return []
            
        node = self.current_dialogue.get(self.current_node, {})
        options = node.get("options", [])
        
        # Filter options based on conditions
        available_options = []
        for idx, option in enumerate(options):
            condition = option.get("condition", {})
            if self.flags.check_condition(condition):
                # Create a copy with index and without condition for display
                display_option = option.copy()
                display_option["index"] = idx  # Add index for selection
                if "condition" in display_option:
                    del display_option["condition"]
                available_options.append(display_option)
                
        return available_options
    
    def select_option(self, option_index):
        """Select a dialogue option by its index"""
        if not self.current_dialogue or not self.current_node:
            return False
            
        node = self.current_dialogue.get(self.current_node, {})
        options = node.get("options", [])
        
        if 0 <= option_index < len(options):
            selected_option = options[option_index]
            
            # Process triggers
            triggers = selected_option.get("triggers", {})
            for key, value in triggers.items():
                self.flags.set_flag(key, value)
            
            # Move to the next node or end dialogue
            next_node = selected_option.get("next_node")
            if next_node == "end":
                self.current_dialogue = None
                self.current_node = None
                return False  # Dialogue ended
            else:
                self.current_node = next_node
                return True  # Continue dialogue
        
        return False