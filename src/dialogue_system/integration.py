"""
Integration helpers for connecting dialogue system to existing game classes.
"""

def add_dialogue_to_station(station_instance, dialogue_id, flags_system=None):
    """
    Adds dialogue capability to an existing SpaceStation instance.
    
    Args:
        station_instance: An existing SpaceStation instance
        dialogue_id: ID of the dialogue file to use
        flags_system: Optional FlagSystem instance (will create one if not provided)
        
    Returns:
        StationDialogueHandler attached to the station
    """
    from .station_dialogue import StationDialogueHandler
    from .flags import FlagSystem
    
    flags = flags_system or FlagSystem()
    
    # Create dialogue handler
    dialogue_handler = StationDialogueHandler(
        station_instance.name if hasattr(station_instance, 'name') else "Unknown Station",
        dialogue_id,
        flags
    )
    
    # Attach the dialogue handler to the station instance
    station_instance._dialogue_handler = dialogue_handler
    
    # Add convenience methods to the station
    def start_dialogue(self):
        return self._dialogue_handler.start_station_dialogue()
    
    def add_npc(self, npc_name, npc_dialogue_id):
        return self._dialogue_handler.add_npc(npc_name, npc_dialogue_id)
    
    def get_npc(self, npc_name):
        return self._dialogue_handler.get_npc(npc_name)
    
    # Add the methods to the station instance
    import types
    station_instance.start_dialogue = types.MethodType(start_dialogue, station_instance)
    station_instance.add_dialogue_npc = types.MethodType(add_npc, station_instance)
    station_instance.get_dialogue_npc = types.MethodType(get_npc, station_instance)
    
    return dialogue_handler