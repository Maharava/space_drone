import pygame
from game_config import *

class ConversationUI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 30)
        
        # Dialog box
        self.bg_rect = pygame.Rect(SCREEN_WIDTH // 6, SCREEN_HEIGHT * 2 // 3, 
                                   SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT // 4)
        
        # Close button
        try:
            self.close_img = pygame.image.load("assets/close.png").convert_alpha()
            self.close_img = pygame.transform.scale(self.close_img, (20, 20))
        except:
            self.close_img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.line(self.close_img, RED, (0, 0), (20, 20), 3)
            pygame.draw.line(self.close_img, RED, (0, 20), (20, 0), 3)
        
        self.close_rect = self.close_img.get_rect(topright=(self.bg_rect.right - 10, self.bg_rect.top + 10))
        
        # Barter button
        self.barter_button = pygame.Rect(self.bg_rect.centerx - 50, self.bg_rect.bottom - 40, 100, 30)
        
        # Speaker and dialog text
        self.speaker = ""
        self.dialog = ""
    
    def set_dialog(self, speaker, text):
        self.speaker = speaker
        self.dialog = text
    
    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, DARK_GREY, self.bg_rect)
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
        
        # Draw speaker name
        speaker_text = self.title_font.render(self.speaker, True, WHITE)
        screen.blit(speaker_text, (self.bg_rect.x + 20, self.bg_rect.y + 15))
        
        # Draw close button
        screen.blit(self.close_img, self.close_rect)
        
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