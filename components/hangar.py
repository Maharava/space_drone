import pygame

class HangarType:
    """Class to define different hangar types"""
    def __init__(self, name, max_size, capacity, power_output):
        self.name = name
        self.max_size = max_size  # Maximum size of items that can be stored
        self.capacity = capacity  # Total capacity of items
        self.power_output = power_output  # Energy produced per second

# Define standard hangar types
HANGAR_BASIC = HangarType("Basic Hangar", 5, 20, 1)
HANGAR_LARGE = HangarType("Large Hangar", 8, 30, 1.5)
HANGAR_POWER = HangarType("Power Hangar", 5, 20, 3)
HANGAR_CARGO = HangarType("Cargo Hangar", 5, 40, 0.8)

class Hangar:
    """Hangar class for managing ship storage and power"""
    def __init__(self, hangar_type=HANGAR_BASIC):
        self.hangar_type = hangar_type
    
    def get_max_size(self):
        """Return the maximum size of items that can be stored"""
        return self.hangar_type.max_size
    
    def get_capacity(self):
        """Return the total capacity of the hangar"""
        return self.hangar_type.capacity
    
    def get_power_output(self):
        """Return the power output of the hangar"""
        return self.hangar_type.power_output
    
    def change_hangar(self, hangar_type):
        """Change to a different hangar type"""
        self.hangar_type = hangar_type