import pygame
from game_config import *
from ui.base_ui import BaseUI

class NPCDialogueUI(BaseUI):
    """UI for NPC dialogue, positioned in the center of the screen."""
    def __init__(self):
        # Center position, medium size
        super().__init__(1/4, 1/4, 1/2, 1/2, title="NPC Dialogue")
        
        # Content
        self.npc_name = ""
        self.dialog_text = ""
        self.options = []
        
        # Layout areas
        self.portrait_rect = pygame.Rect(
            self.bg_rect.x + 20,
            self.bg_rect.y + 60,
            100,
            100
        )
        
        self.text_rect = pygame.Rect(
            self.portrait_rect.right + 20,
            self.bg_rect.y + 60,
            self.bg_rect.right - self.portrait_rect.right - 40,
            self.portrait_rect.height
        )
        
        self.options_rect = pygame.Rect(
            self.bg_rect.x + 20,
            self.portrait_rect.bottom + 20,
            self.bg_rect.width - 40,
            self.bg_rect.bottom - self.portrait_rect.bottom - 40
        )
        
        # Option button tracking
        self.option_buttons = []
    
    def set_dialogue(self, npc_name, text, options=None):
        """Set dialogue content."""
        self.npc_name = npc_name
        self.dialog_text = text
        self.options = options or []
        self.title = f"Speaking with {npc_name}"
    
    def draw(self, screen):
        # Draw background and title
        super().draw(screen)
        
        # Draw portrait area
        pygame.draw.rect(screen, DARK_GREY, self.portrait_rect)
        pygame.draw.rect(screen, WHITE, self.portrait_rect, 2)
        
        # Draw NPC initial
        if self.npc_name:
            initial_font = pygame.font.SysFont(None, 60)
            initial = self.npc_name[0].upper() 
            text = initial_font.render(initial, True, WHITE)
            screen.blit(text, (
                self.portrait_rect.centerx - text.get_width() // 2,
                self.portrait_rect.centery - text.get_height() // 2
            ))
        
        # Draw NPC name
        name_text = self.font.render(self.npc_name, True, WHITE)
        screen.blit(name_text, (
            self.portrait_rect.centerx - name_text.get_width() // 2,
            self.portrait_rect.bottom + 5
        ))
        
        # Draw dialogue text
        self.draw_wrapped_text(screen, self.dialog_text, self.text_rect)
        
        # Draw options divider
        pygame.draw.line(
            screen, WHITE,
            (self.options_rect.left, self.options_rect.top),
            (self.options_rect.right, self.options_rect.top),
            1
        )
        
        # Draw dialogue options
        self.option_buttons = []
        y_pos = self.options_rect.y + 10
        
        for i, option in enumerate(self.options):
            if 'text' in option:
                # Create button
                btn_height = 30
                btn_rect = pygame.Rect(
                    self.options_rect.x + 10,
                    y_pos,
                    self.options_rect.width - 20,
                    btn_height
                )
                
                # Draw button
                pygame.draw.rect(screen, GREY, btn_rect)
                pygame.draw.rect(screen, WHITE, btn_rect, 1)
                
                # Draw number and text
                num_text = self.font.render(f"{i+1}.", True, YELLOW)
                screen.blit(num_text, (btn_rect.x + 5, btn_rect.y + 5))
                
                option_text = self.font.render(option['text'], True, WHITE)
                screen.blit(option_text, (btn_rect.x + 35, btn_rect.y + 5))
                
                # Store for click detection
                self.option_buttons.append((btn_rect, i))
                
                y_pos += btn_height + 5
    
    def draw_wrapped_text(self, screen, text, rect):
        """Draw text wrapped to fit in rectangle."""
        y = rect.y
        words = text.split(' ')
        line = ""
        
        for word in words:
            test_line = line + word + " "
            size = self.font.size(test_line)
            
            if size[0] > rect.width:
                # Draw current line and start new one
                if line:
                    text_surf = self.font.render(line, True, WHITE)
                    screen.blit(text_surf, (rect.x, y))
                    y += self.font.get_linesize()
                    
                    # Check if we're out of space
                    if y + self.font.get_linesize() > rect.bottom:
                        screen.blit(self.font.render("...", True, WHITE), (rect.x, y))
                        return
                
                line = word + " "
            else:
                line = test_line
        
        # Draw final line
        if line:
            text_surf = self.font.render(line, True, WHITE)
            screen.blit(text_surf, (rect.x, y))
    
    def handle_click(self, pos):
        # Handle base UI clicks (close button)
        result = super().handle_click(pos)
        if result:
            return result
        
        # Check option buttons
        for rect, index in self.option_buttons:
            if rect.collidepoint(pos):
                return {"action": "select_option", "index": index}
        
        return None