import pygame
from game_config import *
from ui.base_ui import BaseUI

class ConversationUI(BaseUI):
    def __init__(self):
        # Use different dimensions for conversation UI (wider and shorter)
        super().__init__(1/6, 2/3, 2/3, 1/4)
        
        # Speaker and dialog text
        self.speaker = ""
        self.dialog = ""
        
        # Barter button
        self.barter_button = pygame.Rect(self.bg_rect.centerx - 50, self.bg_rect.bottom - 40, 100, 30)
    
    def set_dialog(self, speaker, text):
        self.speaker = speaker
        self.dialog = text
    
    def draw(self, screen):
        # Draw background
        self.draw_background(screen)
        
        # Draw speaker name
        speaker_text = self.title_font.render(self.speaker, True, WHITE)
        screen.blit(speaker_text, (self.bg_rect.x + 20, self.bg_rect.y + 15))
        
        # Draw close button
        self.draw_close_button(screen)
        
        # Draw dialog text (with word wrap)
        words = self.dialog.split(' ')
        line = ""
        y_offset = 50
        for word in words:
            test_line = line + word + " "
            test_surf = self.font.render(test_line, True, WHITE)
            if test_surf.get_width() < self.bg_rect.width - 40:
                line = test_line
            else:
                text_surf = self.font.render(line, True, WHITE)
                screen.blit(text_surf, (self.bg_rect.x + 20, self.bg_rect.y + y_offset))
                y_offset += 25
                line = word + " "
        
        if line:
            text_surf = self.font.render(line, True, WHITE)
            screen.blit(text_surf, (self.bg_rect.x + 20, self.bg_rect.y + y_offset))
        
        # Draw barter button
        pygame.draw.rect(screen, BLUE, self.barter_button)
        pygame.draw.rect(screen, WHITE, self.barter_button, 1)
        
        barter_text = self.font.render("Barter", True, WHITE)
        screen.blit(barter_text, (self.barter_button.centerx - barter_text.get_width() // 2,
                                 self.barter_button.centery - barter_text.get_height() // 2))
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"
        
        # Check if barter button clicked
        if self.barter_button.collidepoint(pos):
            return "barter"
            
        return False