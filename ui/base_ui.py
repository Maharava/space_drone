import pygame
from game_config import *

class BaseUI:
    def __init__(self, x_fraction=1/6, y_fraction=1/6, width_fraction=2/3, height_fraction=2/3):
        # UI rectangle
        self.bg_rect = pygame.Rect(
            SCREEN_WIDTH * x_fraction, 
            SCREEN_HEIGHT * y_fraction,
            SCREEN_WIDTH * width_fraction, 
            SCREEN_HEIGHT * height_fraction
        )
        
        # Common font setup
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 30)
        
        # Close button
        try:
            self.close_img = pygame.image.load("assets/close.png").convert_alpha()
            self.close_img = pygame.transform.scale(self.close_img, (20, 20))
        except:
            self.close_img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.line(self.close_img, RED, (0, 0), (20, 20), 3)
            pygame.draw.line(self.close_img, RED, (0, 20), (20, 0), 3)
        
        self.close_rect = self.close_img.get_rect(topright=(self.bg_rect.right - 10, self.bg_rect.top + 10))
        
        # Tooltip
        self.hover_item = None
    
    def draw_background(self, screen):
        # Draw background panel
        pygame.draw.rect(screen, DARK_GREY, self.bg_rect)
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
    
    def draw_title(self, screen, title_text):
        # Draw title text
        title = self.title_font.render(title_text, True, WHITE)
        screen.blit(title, (self.bg_rect.centerx - title.get_width() // 2, self.bg_rect.top + 15))
    
    def draw_close_button(self, screen):
        # Draw close button
        screen.blit(self.close_img, self.close_rect)
    
    def draw(self, screen):
        self.draw_background(screen)
        self.draw_close_button(screen)
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"
        return False
        
    def draw_tooltip(self, screen, text, mouse_pos):
        # Create tooltip background
        tooltip_bg = pygame.Surface((300, 60))
        tooltip_bg.set_alpha(200)
        tooltip_bg.fill((30, 30, 30))
        
        tooltip_rect = tooltip_bg.get_rect(topleft=(mouse_pos[0] + 10, mouse_pos[1] + 10))
        
        # Make sure tooltip doesn't go off screen
        if tooltip_rect.right > SCREEN_WIDTH:
            tooltip_rect.right = SCREEN_WIDTH - 5
        if tooltip_rect.bottom > SCREEN_HEIGHT:
            tooltip_rect.bottom = SCREEN_HEIGHT - 5
            
        screen.blit(tooltip_bg, tooltip_rect)
        
        # Word wrap text
        words = text.split()
        line = ""
        y_pos = tooltip_rect.y + 10
        
        for word in words:
            test_line = line + word + " "
            test_width = self.small_font.size(test_line)[0]
            
            if test_width < tooltip_rect.width - 20:
                line = test_line
            else:
                text_surf = self.small_font.render(line, True, SILVER)
                screen.blit(text_surf, (tooltip_rect.x + 10, y_pos))
                y_pos += 20
                line = word + " "
        
        if line:
            text_surf = self.small_font.render(line, True, SILVER)
            screen.blit(text_surf, (tooltip_rect.x + 10, y_pos))