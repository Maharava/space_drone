import pygame
from game_config import *

class JumpUI:
    """UI element for displaying jump prompts"""
    def __init__(self, map_system):
        self.map_system = map_system
        self.font = pygame.font.SysFont(None, 28)
        self.small_font = pygame.font.SysFont(None, 20)
        
        # Jump popup properties
        self.visible = False
        self.direction = None
        self.target_area = None
        
        # Create UI elements
        self.prompt_bg = pygame.Surface((300, 60))
        self.prompt_bg.set_alpha(200)
        self.prompt_bg.fill(DARK_GREY)
        self.bg_rect = self.prompt_bg.get_rect(
            midbottom=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20)
        )
    
    def update(self, player_position):
        """Update jump UI state based on player position"""
        # Check if player can jump
        can_jump_dir = self.map_system.can_jump(player_position)
        if can_jump_dir:
            # Check if there's a connection in this direction
            target_area_id = self.map_system.get_connection(can_jump_dir)
            if target_area_id:
                self.visible = True
                self.direction = can_jump_dir
                self.target_area = target_area_id
                return
        
        # No valid jump available
        self.visible = False
        self.direction = None
        self.target_area = None
    
    def draw(self, screen):
        """Draw the jump UI if visible"""
        if not self.visible:
            return
        
        # Draw background
        screen.blit(self.prompt_bg, self.bg_rect)
        
        # Draw border
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
        
        # Direction text
        direction_text = self.direction.capitalize()
        dir_text_surf = self.font.render(f"Jump {direction_text}", True, WHITE)
        
        # Target area text
        if self.target_area and self.target_area in self.map_system.areas:
            area_name = self.map_system.areas[self.target_area].get("name", self.target_area)
            target_text = f"to {area_name}"
        else:
            target_text = "to Unknown Area"
        
        target_surf = self.small_font.render(target_text, True, SILVER)
        
        # Draw text
        screen.blit(dir_text_surf, 
                   (self.bg_rect.centerx - dir_text_surf.get_width() // 2, 
                    self.bg_rect.top + 10))
        screen.blit(target_surf, 
                   (self.bg_rect.centerx - target_surf.get_width() // 2,
                    self.bg_rect.top + 35))
    
    def handle_jump(self):
        """Process jump if conditions are met"""
        if not self.visible or not self.target_area:
            return False, None
        
        # Execute the jump
        return self.map_system.change_area(self.target_area, self.direction)