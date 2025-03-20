import pygame

class Hangar:
    """Hangar class for managing ship storage and power"""
    def __init__(self, module):
        self.module = module
    
    def get_max_size(self):
        """Return the maximum size of items that can be stored"""
        if self.module and hasattr(self.module, 'stats'):
            return self.module.stats.get('max_size', 5)  # Default if not specified
        return 5
    
    def get_capacity(self):
        """Return the total capacity of the hangar"""
        if self.module and hasattr(self.module, 'stats'):
            return self.module.stats.get('capacity', 4)  # Default if not specified
        return 4
    
    def get_power_output(self):
        """Return the power output of the hangar"""
        if self.module and hasattr(self.module, 'stats'):
            return self.module.stats.get('energy_output', 1.0)  # Default if not specified
        return 1.0
    
    def change_hangar(self, module):
        """Change to a different hangar module"""
        self.module = module