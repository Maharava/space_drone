import pygame
from game_config import *
from ui.base_ui import BaseUI

class JobsBoardUI(BaseUI):
    """UI for displaying available quests"""
    def __init__(self, game):
        super().__init__(1/6, 1/6, 2/3, 2/3, title="Jobs Board")
        self.game = game
        
        # Quest list area
        self.quest_area = pygame.Rect(
            self.bg_rect.x + 20,
            self.bg_rect.y + 60,
            self.bg_rect.width - 40,
            self.bg_rect.height - 100
        )
        
        # Quest buttons
        self.quest_buttons = []
        self.update_quests()
        
    def update_quests(self):
        """Update the list of available quests"""
        self.quest_buttons = []
        
        # Check if quest manager exists
        if not hasattr(self.game, 'quest_manager'):
            return
        
        # Check current station
        station = self.game.map_system.get_nearest_station(self.game.player.position)
        if not station:
            return
            
        # Add Copernicus Station quests
        if station.name == "Copernicus Station":
            # Mining Task
            mining_status = self.game.quest_manager.flags.get_flag("mining_quest", 0)
            
            # Get status info
            status_text = self.get_quest_status_text(mining_status)
            status_color = self.get_quest_status_color(mining_status)
            
            # Create quest button
            button_rect = pygame.Rect(
                self.quest_area.x,
                self.quest_area.y,
                self.quest_area.width,
                60
            )
            
            # Add to button list
            self.quest_buttons.append({
                "rect": button_rect,
                "name": "Mining Task",
                "description": "Collect 5 rare ore for the Mining Foreman.",
                "npc": "Mining Foreman",
                "status": status_text,
                "color": status_color,
                "status_code": mining_status
            })
    
    def get_quest_status_text(self, status_code):
        """Get display text for quest status."""
        if status_code == 0:
            return "Available"
        elif status_code == 1:
            # In progress - show ore count
            if hasattr(self.game, 'quest_manager'):
                return self.game.quest_manager.get_mining_quest_progress()
            return "In Progress"
        elif status_code == 2:
            return "Completed"
        else:
            return "Failed"
    
    def get_quest_status_color(self, status_code):
        """Get color for quest status."""
        if status_code == 0:
            return WHITE  # Available
        elif status_code == 1:
            return YELLOW  # In Progress
        elif status_code == 2:
            return GREEN  # Completed
        else:
            return RED  # Failed
            
    def draw(self, screen):
        # Draw base UI
        super().draw(screen)
        
        # Draw quest area background
        pygame.draw.rect(screen, DARK_GREY, self.quest_area)
        pygame.draw.rect(screen, WHITE, self.quest_area, 1)
        
        # Draw quest buttons
        if not self.quest_buttons:
            # No quests available
            no_quests_text = self.font.render("No jobs available at this station.", True, WHITE)
            screen.blit(no_quests_text, (
                self.quest_area.centerx - no_quests_text.get_width() // 2,
                self.quest_area.centery - no_quests_text.get_height() // 2
            ))
        else:
            for i, quest in enumerate(self.quest_buttons):
                # Draw button
                pygame.draw.rect(screen, GREY, quest["rect"])
                pygame.draw.rect(screen, quest["color"], quest["rect"], 2)
                
                # Draw quest name
                name_text = self.font.render(quest["name"], True, WHITE)
                screen.blit(name_text, (quest["rect"].x + 10, quest["rect"].y + 10))
                
                # Draw description
                desc_text = self.small_font.render(quest["description"], True, SILVER)
                screen.blit(desc_text, (quest["rect"].x + 10, quest["rect"].y + 35))
                
                # Draw status
                status_text = self.small_font.render(f"Status: {quest['status']}", True, quest["color"])
                screen.blit(status_text, (
                    quest["rect"].right - status_text.get_width() - 10,
                    quest["rect"].y + 10
                ))
                
                # Draw talk button if not completed
                if quest["status_code"] != 2:  # Not completed
                    talk_rect = pygame.Rect(
                        quest["rect"].right - 70,
                        quest["rect"].bottom - 25,
                        60, 20
                    )
                    pygame.draw.rect(screen, BLUE, talk_rect)
                    
                    talk_text = self.small_font.render("Talk", True, WHITE)
                    screen.blit(talk_text, (
                        talk_rect.centerx - talk_text.get_width() // 2,
                        talk_rect.centery - talk_text.get_height() // 2
                    ))
                    
                    # Store talk button rect
                    quest["talk_rect"] = talk_rect
    
    def handle_click(self, pos):
        # Check base UI clicks
        result = super().handle_click(pos)
        if result:
            return result
            
        # Check quest talk buttons
        for quest in self.quest_buttons:
            if "talk_rect" in quest and quest["talk_rect"].collidepoint(pos):
                return {"action": "talk_quest", "npc": quest["npc"]}
                
        return None