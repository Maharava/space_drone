import json
import os

class FlagSystem:
    """Simple flag system to track game state."""
    def __init__(self, flags_file="flags/game_flags.json"):
        self.flags_file = flags_file
        self.flags = {}
        self.load_flags()
    
    def load_flags(self):
        """Load flags from file."""
        try:
            if os.path.exists(self.flags_file):
                with open(self.flags_file, 'r') as f:
                    self.flags = json.load(f)
                    print(f"Loaded flags: {self.flags}")
        except Exception as e:
            print(f"Error loading flags: {e}")
            # Continue with empty flags if file can't be loaded
    
    def save_flags(self):
        """Save flags to file."""
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(self.flags_file), exist_ok=True)
            with open(self.flags_file, 'w') as f:
                json.dump(self.flags, f, indent=4)
        except Exception as e:
            print(f"Error saving flags: {e}")
    
    def get_flag(self, flag_name, default=0):
        """Get flag value."""
        return self.flags.get(flag_name, default)
    
    def set_flag(self, flag_name, value):
        """Set flag value and save immediately."""
        self.flags[flag_name] = value
        self.save_flags()
    
    def increment_flag(self, flag_name, amount=1):
        """Increment a numeric flag."""
        current_value = self.get_flag(flag_name, 0)
        self.flags[flag_name] = current_value + amount
        self.save_flags()