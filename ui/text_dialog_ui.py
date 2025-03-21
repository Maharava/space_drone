import pygame
from game_config import *
from ui.base_ui import BaseUI

class TextDialogUI(BaseUI):
    """UI for displaying longer text with scrolling"""
    def __init__(self, title="Text", text=""):
        # Larger UI for text
        super().__init__(1/8, 1/8, 3/4, 3/4, title)
        
        # Text content
        self.set_text(text)
        
        # Scrolling
        self.scroll_pos = 0
        self.max_scroll = 0
        
        # Scroll buttons
        button_size = 30
        self.scroll_up_btn = pygame.Rect(
            self.bg_rect.right - button_size - 10, 
            self.bg_rect.y + 50, 
            button_size, button_size
        )
        self.scroll_down_btn = pygame.Rect(
            self.bg_rect.right - button_size - 10, 
            self.bg_rect.bottom - button_size - 10, 
            button_size, button_size
        )
        
        # Add buttons to clickable elements
        self.add_clickable("scroll_up", self.scroll_up_btn)
        self.add_clickable("scroll_down", self.scroll_down_btn)
        
    def set_text(self, text):
        """Set the text and pre-process it for rendering"""
        self.text = text
        self.text_lines = []
        
        # Calculate text wrap
        words = text.split()
        if not words:
            return
            
        # Estimate width (excluding margins and scroll buttons)
        max_width = self.bg_rect.width - 60
        
        line = ""
        for word in words:
            test_line = line + word + " "
            test_surf = self.font.render(test_line, True, WHITE)
            
            if test_surf.get_width() < max_width:
                line = test_line
            else:
                self.text_lines.append(line)
                line = word + " "
        
        if line:
            self.text_lines.append(line)
        
        # Calculate max scroll based on lines
        line_height = 25
        content_height = len(self.text_lines) * line_height
        visible_height = self.bg_rect.height - 100  # Account for title and margins
        
        self.max_scroll = max(0, content_height - visible_height)
    
    def scroll(self, amount):
        """Scroll the text by amount"""
        self.scroll_pos = max(0, min(self.max_scroll, self.scroll_pos + amount))
    
    def draw(self, screen):
        # Draw base UI
        super().draw(screen)
        
        # Draw text content
        line_height = 25
        y_offset = 60 - self.scroll_pos  # Start below title, adjusted for scroll
        
        # Create clipping rectangle for text area
        content_rect = pygame.Rect(
            self.bg_rect.x + 20, 
            self.bg_rect.y + 50, 
            self.bg_rect.width - 60,  # Leave room for scroll buttons
            self.bg_rect.height - 100  # Leave room for title and bottom margin
        )
        
        # Set clipping rectangle
        old_clip = screen.get_clip()
        screen.set_clip(content_rect)
        
        # Draw visible lines
        for line in self.text_lines:
            if y_offset + line_height >= self.bg_rect.y + 50:
                text_surf = self.font.render(line, True, WHITE)
                screen.blit(text_surf, (self.bg_rect.x + 20, self.bg_rect.y + y_offset))
            
            y_offset += line_height
            
            if y_offset > self.bg_rect.y + self.bg_rect.height - 50:
                break
        
        # Reset clipping rectangle
        screen.set_clip(old_clip)
        
        # Draw scroll buttons if needed
        if self.max_scroll > 0:
            # Up button
            pygame.draw.rect(screen, GREY, self.scroll_up_btn)
            pygame.draw.polygon(screen, WHITE, [
                (self.scroll_up_btn.centerx, self.scroll_up_btn.y + 5),
                (self.scroll_up_btn.x + 5, self.scroll_up_btn.y + 25),
                (self.scroll_up_btn.right - 5, self.scroll_up_btn.y + 25)
            ])
            
            # Down button
            pygame.draw.rect(screen, GREY, self.scroll_down_btn)
            pygame.draw.polygon(screen, WHITE, [
                (self.scroll_down_btn.centerx, self.scroll_down_btn.bottom - 5),
                (self.scroll_down_btn.x + 5, self.scroll_down_btn.y + 5),
                (self.scroll_down_btn.right - 5, self.scroll_down_btn.y + 5)
            ])
            
            # Scroll indicator
            total_height = self.bg_rect.height - 100
            visible_height = total_height
            indicator_height = max(30, visible_height * (visible_height / (len(self.text_lines) * line_height)))
            indicator_pos = (self.scroll_pos / self.max_scroll) * (total_height - indicator_height)
            
            indicator_rect = pygame.Rect(
                self.scroll_up_btn.x - 10, 
                self.bg_rect.y + 50 + indicator_pos,
                5, indicator_height
            )
            pygame.draw.rect(screen, WHITE, indicator_rect)
    
    def handle_click(self, pos):
        # Base UI click handling
        result = super().handle_click(pos)
        if result:
            return result
        
        # Scroll buttons
        if self.scroll_up_btn.collidepoint(pos):
            self.scroll(-50)  # Scroll up 50 pixels
            return "scroll"
            
        if self.scroll_down_btn.collidepoint(pos):
            self.scroll(50)  # Scroll down 50 pixels
            return "scroll"
            
        return None
        
    def handle_event(self, event):
        """Handle pygame events, particularly mouse wheel"""
        if event.type == pygame.MOUSEWHEEL:
            self.scroll(-event.y * 25)  # Scroll 25 pixels per wheel notch
            return True
        return False