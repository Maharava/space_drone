import json
import os

class FlagSystem:
    def __init__(self, flags_file="flags.json"):
        self.flags_file = flags_file
        self.flags = self._load_flags()
    
    def _load_flags(self):
        """Load flags from file or create new if file doesn't exist"""
        if os.path.exists(self.flags_file):
            with open(self.flags_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_flags(self):
        """Save flags to file"""
        with open(self.flags_file, 'w') as f:
            json.dump(self.flags, f, indent=4)
    
    def get_flag(self, flag_name, default=None):
        """Get a flag value"""
        return self.flags.get(flag_name, default)
    
    def set_flag(self, flag_name, value):
        """Set a flag value"""
        self.flags[flag_name] = value
        self.save_flags()
    
    def increment_flag(self, flag_name, amount=1):
        """Increment a numeric flag"""
        current_value = self.get_flag(flag_name, 0)
        self.set_flag(flag_name, current_value + amount)
    
    def check_condition(self, condition):
        """Check if a condition is met based on flags
        Condition format: {"flag_name": value}
        """
        if not condition:
            return True  # Empty condition is always met
            
        for flag_name, required_value in condition.items():
            if self.get_flag(flag_name) != required_value:
                return False
        return True