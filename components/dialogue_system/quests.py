import json
import os
from .flags import FlagSystem

class QuestSystem:
    def __init__(self, quests_folder="quests", flags_system=None):
        self.quests_folder = quests_folder
        self.flags = flags_system or FlagSystem()
        self.active_quests = {}
        
        # Create quests folder if it doesn't exist
        os.makedirs(quests_folder, exist_ok=True)
    
    def load_quest(self, quest_name):
        """Load a quest file"""
        file_path = os.path.join(self.quests_folder, f"{quest_name}.json")
        if not os.path.exists(file_path):
            print(f"Quest file not found: {file_path}")
            return False
            
        try:
            with open(file_path, 'r') as f:
                quest_data = json.load(f)
            self.active_quests[quest_name] = quest_data
            return True
        except json.JSONDecodeError:
            print(f"Error parsing quest file: {file_path}")
            return False
    
    def start_quest(self, quest_name):
        """Start a quest by loading it and setting initial flags"""
        if not self.load_quest(quest_name):
            return False
            
        quest_data = self.active_quests.get(quest_name, {})
        
        # Set initial quest flags
        self.flags.set_flag(f"{quest_name}_started", True)
        self.flags.set_flag(f"{quest_name}_completed", False)
        
        # Set any quest-specific initial flags
        initial_flags = quest_data.get("initial_flags", {})
        for flag_name, value in initial_flags.items():
            self.flags.set_flag(flag_name, value)
            
        # Save flags to disk
        self.flags.save_flags()
        return True
    
    def update_quest_progress(self, quest_name, flag_name, value=None):
        """Update a specific quest flag"""
        if value is not None:
            self.flags.set_flag(flag_name, value)
        else:
            # Increment numeric flags by default
            self.flags.increment_flag(flag_name)
            
        # Don't save immediately to avoid lag
        return True
    
    def complete_quest(self, quest_name):
        """Mark a quest as completed"""
        if quest_name not in self.active_quests:
            return False
            
        self.flags.set_flag(f"{quest_name}_completed", True)
        
        # Process completion rewards or triggers
        quest_data = self.active_quests.get(quest_name, {})
        rewards = quest_data.get("rewards", {})
        
        # Handle rewards
        for reward_type, value in rewards.items():
            if reward_type == "silver":
                # This is a placeholder - actual reward handled by quest_manager
                pass
            elif reward_type == "flags":
                # Set flags as rewards
                for flag_name, flag_value in value.items():
                    self.flags.set_flag(flag_name, flag_value)
        
        # Save flags to disk after completing quest
        self.flags.save_flags()
        return True
    
    def get_quest_status(self, quest_name):
        """Get the status of a quest"""
        if quest_name not in self.active_quests:
            return None
            
        started = self.flags.get_flag(f"{quest_name}_started", False)
        completed = self.flags.get_flag(f"{quest_name}_completed", False)
        
        if not started:
            return "not_started"
        elif completed:
            return "completed"
        else:
            return "in_progress"
    
    def get_active_quests(self):
        """Get a list of all active (started but not completed) quests"""
        active = []
        for quest_name in self.active_quests:
            status = self.get_quest_status(quest_name)
            if status == "in_progress":
                active.append(quest_name)
        return active