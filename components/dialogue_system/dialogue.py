import json
import os

class DialogueSystem:
    """Simple dialogue system to handle NPC conversations."""
    def __init__(self, flags_system, game_ref=None):
        self.flags = flags_system
        self.game = game_ref
        self.current_dialogue = None
        self.current_node = None
    
    def load_dialogue(self, dialogue_id):
        """Load dialogue file and set starting node."""
        try:
            file_path = f"dialogue/{dialogue_id}.json"
            if not os.path.exists(file_path):
                print(f"Dialogue file not found: {file_path}")
                return False
                
            with open(file_path, 'r') as f:
                self.current_dialogue = json.load(f)
            
            # Determine starting node based on quest state
            if dialogue_id == "mining_foreman_dialogue":
                quest_status = self.flags.get_flag("mining_quest", 0)
                if quest_status == 0:
                    # Not started
                    self.current_node = "root"
                    print("Starting at root node (quest not started)")
                elif quest_status == 1:
                    # In progress
                    self.current_node = "check_progress"
                    print("Starting at check_progress node (quest in progress)")
                elif quest_status >= 2:
                    # Completed
                    self.current_node = "completed"
                    print("Starting at completed node (quest finished)")
            else:
                # Default to root node for other dialogues
                self.current_node = "root"
            
            return True
        except Exception as e:
            print(f"Error loading dialogue: {e}")
            return False
    
    def get_current_node_text(self):
        """Get the text for current dialogue node."""
        if not self.current_dialogue or not self.current_node:
            return "No dialogue available."
            
        node = self.current_dialogue.get(self.current_node, {})
        return node.get("npc_text", "...")
    
    def get_available_options(self):
        """Get options for current dialogue node with conditional filtering."""
        if not self.current_dialogue or not self.current_node:
            return []
            
        node = self.current_dialogue.get(self.current_node, {})
        options = node.get("options", [])
        
        # Filter options based on conditions
        available_options = []
        for idx, option in enumerate(options):
            condition = option.get("condition", {})
            
            # Check if condition is met
            condition_met = True
            for flag_name, required_value in condition.items():
                # Special case for ore check
                if flag_name == "has_enough_ore" and self.game:
                    # Check player inventory for 5+ rare ore
                    has_enough = self.check_player_has_enough_ore()
                    if has_enough != required_value:
                        condition_met = False
                        break
                elif self.flags.get_flag(flag_name) != required_value:
                    condition_met = False
                    break
            
            if condition_met:
                # Add option with index for selection
                option_copy = option.copy()
                option_copy["index"] = idx
                if "condition" in option_copy:
                    del option_copy["condition"]  # Remove condition from display
                available_options.append(option_copy)
        
        return available_options
    
    def check_player_has_enough_ore(self):
        """Check if player has enough rare ore in inventory."""
        try:
            if not self.game or not hasattr(self.game, "player"):
                return False
                
            rare_ore_count = 0
            
            # Check inventory for Rare Ore
            for row in self.game.player.inventory:
                for slot in row:
                    if slot["item"] and slot["item"].name == "Rare Ore":
                        rare_ore_count += slot["count"]
            
            print(f"Player has {rare_ore_count} Rare Ore")
            return rare_ore_count >= 5
        except Exception as e:
            print(f"Error checking ore: {e}")
            return False
    
    def select_option(self, option_index):
        """Select dialogue option and process triggers."""
        if not self.current_dialogue or not self.current_node:
            return False
            
        node = self.current_dialogue.get(self.current_node, {})
        options = node.get("options", [])
        
        if 0 <= option_index < len(options):
            selected_option = options[option_index]
            
            # Process triggers - update flags
            triggers = selected_option.get("triggers", {})
            for flag_name, value in triggers.items():
                print(f"Setting flag: {flag_name} = {value}")
                self.flags.set_flag(flag_name, value)
            
            # Handle ore removal if completing mining quest
            if "mining_quest" in triggers and triggers["mining_quest"] == 2:
                self.remove_rare_ore_from_inventory()
                
                # Add reward
                if self.game and hasattr(self.game, "player"):
                    self.game.player.stats.silver += 50
                    print("Mining quest completed! Awarded 50 silver.")
            
            # Move to next node or end dialogue
            next_node = selected_option.get("next_node")
            if next_node == "end":
                self.current_node = None
                return False  # Dialogue ended
            else:
                self.current_node = next_node
                return True  # Continue dialogue
        
        return False
    
    def remove_rare_ore_from_inventory(self):
        """Remove 5 Rare Ore from player inventory when completing quest."""
        try:
            if not self.game or not hasattr(self.game, "player"):
                return
                
            ore_to_remove = 5
            
            # Remove ore from inventory slots
            for row in self.game.player.inventory:
                for slot in row:
                    if slot["item"] and slot["item"].name == "Rare Ore" and ore_to_remove > 0:
                        if slot["count"] <= ore_to_remove:
                            # Remove entire stack
                            ore_to_remove -= slot["count"]
                            slot["count"] = 0
                            slot["item"] = None
                        else:
                            # Remove partial stack
                            slot["count"] -= ore_to_remove
                            ore_to_remove = 0
                        
                        # Update total ore count
                        self.game.player.total_ore -= 5
                        
                        if ore_to_remove == 0:
                            break
                
                if ore_to_remove == 0:
                    break
            
            print("Removed 5 Rare Ore from inventory")
        except Exception as e:
            print(f"Error removing ore: {e}")