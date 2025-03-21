import pygame
from game_config import *
from ui.base_ui import BaseUI

class ConversationUI(BaseUI):
    def __init__(self):
        # Wider and shorter UI for conversations
        super().__init__(1/6, 2/3, 2/3, 1/4)
        
        # Speaker and dialog text
        self.speaker = ""
        self.dialog = ""
        self.options = []
        
        # Barter button (right side)
        self.barter_button = pygame.Rect(self.bg_rect.right - 120, self.bg_rect.bottom - 40, 100, 30)
        
        # Jobs Board button (left side)
        self.jobs_button = pygame.Rect(self.bg_rect.x + 20, self.bg_rect.bottom - 40, 100, 30)
        
        # Add buttons to clickable elements
        self.add_clickable("barter", self.barter_button)
        self.add_clickable("jobs", self.jobs_button)
    
    def set_dialog(self, speaker, text, options=None):
        self.speaker = speaker
        self.dialog = text
        self.options = options or []
    
    def draw(self, screen):
        # Draw background
        self.draw_background(screen)
        
        # Draw speaker name
        speaker_text = self.title_font.render(self.speaker, True, WHITE)
        screen.blit(speaker_text, (self.bg_rect.x + 20, self.bg_rect.y + 15))
        
        # Draw close button
        self.draw_close_button(screen)
        
        # Calculate dialog area
        dialog_area_height = self.bg_rect.height - 140  # Leave room for speaker and buttons
        max_y_offset = self.bg_rect.y + 50 + dialog_area_height
        
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
                
                # Check if we're running out of space
                if self.bg_rect.y + y_offset > max_y_offset:
                    text_surf = self.font.render("...", True, WHITE)
                    screen.blit(text_surf, (self.bg_rect.x + 20, self.bg_rect.y + y_offset))
                    break
        
        if line and self.bg_rect.y + y_offset <= max_y_offset:
            text_surf = self.font.render(line, True, WHITE)
            screen.blit(text_surf, (self.bg_rect.x + 20, self.bg_rect.y + y_offset))
            y_offset += 30
        
        # Draw options
        for i, option in enumerate(self.options):
            if 'text' in option and self.bg_rect.y + y_offset <= max_y_offset:
                option_text = self.font.render(f"{i+1}. {option['text']}", True, WHITE)
                screen.blit(option_text, (self.bg_rect.x + 40, self.bg_rect.y + y_offset))
                y_offset += 30
        
        # Draw barter button
        pygame.draw.rect(screen, BLUE, self.barter_button)
        pygame.draw.rect(screen, WHITE, self.barter_button, 1)
        
        barter_text = self.font.render("Barter", True, WHITE)
        screen.blit(barter_text, (self.barter_button.centerx - barter_text.get_width() // 2,
                                 self.barter_button.centery - barter_text.get_height() // 2))
        
        # Draw jobs board button
        pygame.draw.rect(screen, GREEN, self.jobs_button)
        pygame.draw.rect(screen, WHITE, self.jobs_button, 1)
        
        jobs_text = self.font.render("Jobs", True, WHITE)
        screen.blit(jobs_text, (self.jobs_button.centerx - jobs_text.get_width() // 2,
                               self.jobs_button.centery - jobs_text.get_height() // 2))
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"
        
        # Check if barter button clicked
        if self.barter_button.collidepoint(pos):
            return "barter"
            
        # Check if jobs button clicked
        if self.jobs_button.collidepoint(pos):
            return "jobs"
            
        return None