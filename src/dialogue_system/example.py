from src.dialogue_system.station_dialogue import StationDialogueHandler
from src.dialogue_system.npc_interaction import NPCInteraction
from src.dialogue_system.flags import FlagSystem
from src.dialogue_system.quests import QuestSystem

def main():
    # Initialize systems
    flags = FlagSystem()
    quest_system = QuestSystem(flags_system=flags)
    interaction = NPCInteraction()
    
    # Load the mining quest
    quest_system.start_quest("mining_quest")
    
    # Create Copernicus Station dialogue handler
    copernicus_dialogue = StationDialogueHandler("Copernicus Station", "copernicus_station", flags)
    
    # Add mining foreman NPC
    copernicus_dialogue.add_npc("Mining Foreman", "copernicus_mining_foreman")