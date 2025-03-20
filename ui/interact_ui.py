import pygame
from game_config import *

class InteractUI:
    """UI element for displaying interaction prompts"""
    def __init__(self):
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Interaction popup properties
        self.visible = False
        self.target_name = None
        
        # Create UI elements
        self.prompt_bg = pygame.Surface((300, 60))
        self.prompt_bg.set_alpha(200)
        self.prompt_bg.fill(DARK_GREY)
        self.bg_rect = self.prompt_bg.get_rect(
            midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 90)  # Higher than jump UI
        )
    
    def update(self, is_near_station, station_name=None):
        """Update interaction UI based on proximity to interactive objects"""
        if is_near_station and station_name:
            self.visible = True
            self.target_name = station_name
        else:
            self.visible = False
            self.target_name = None
    
    def draw(self, screen):
        """Draw the interaction UI if visible"""
        if not self.visible:
            return
        
        # Draw background
        screen.blit(self.prompt_bg, self.bg_rect)
        
        # Draw border
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
        
        # Draw text
        interact_text = self.font.render("Press E to Interact", True, WHITE)
        
        # Target name text
        if self.target_name:
            target_surf = self.small_font.render(f"with {self.target_name}", True, SILVER)
        else:
            target_surf = self.small_font.render("", True, SILVER)
        
        # Draw text
        screen.blit(interact_text, 
                   (self.bg_rect.centerx - interact_text.get_width() // 2, 
                    self.bg_rect.top + 10))
        screen.blit(target_surf, 
                   (self.bg_rect.centerx - target_surf.get_width() // 2,
                    self.bg_rect.top + 35))