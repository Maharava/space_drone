import pygame
from game_config import *
from ui.base_ui import BaseUI

class NPCDialogueUI(BaseUI):
    """UI for NPC dialogue, positioned in the center of the screen"""
    def __init__(self):
        # Center position, medium size
        super().__init__(1/4, 1/4, 1/2, 1/2, title="NPC Dialogue")
        
        # Text properties
        self.npc_name = ""
        self.dialog_text = ""
        self.options = []
        
        # NPC portrait area - left side of dialogue
        portrait_size = min(120, self.bg_rect.height // 3)
        self.portrait_rect = pygame.Rect(
            self.bg_rect.x + 20,
            self.bg_rect.y + 60,
            portrait_size,
            portrait_size
        )
        
        # Dialog text area - right of portrait
        self.text_rect = pygame.Rect(
            self.portrait_rect.right + 20,
            self.bg_rect.y + 60,
            self.bg_rect.right - self.portrait_rect.right - 40,
            self.portrait_rect.height
        )
        
        # Options area - below portrait and text
        self.options_rect = pygame.Rect(
            self.bg_rect.x + 20,
            self.portrait_rect.bottom + 20,
            self.bg_rect.width - 40,
            self.bg_rect.bottom - self.portrait_rect.bottom - 40
        )
        
        # Track option buttons
        self.option_buttons = []
    
    def set_dialogue(self, npc_name, text, options=None):
        """Set the dialogue content"""
        self.npc_name = npc_name
        self.dialog_text = text
        self.options = options or []
        
        # Update title
        self.title = f"Speaking with {npc_name}"
        
        # Reset option buttons
        self.option_buttons = []
    
    def draw(self, screen):
        # Draw base UI with title
        super().draw(screen)
        
        # Draw NPC portrait
        pygame.draw.rect(screen, GREY, self.portrait_rect)
        pygame.draw.rect(screen, WHITE, self.portrait_rect, 2)
        
        # Draw NPC initial inside portrait
        initial_font = pygame.font.SysFont(None, 60)
        if self.npc_name:
            initial = self.npc_name[0].upper()
            initial_surf = initial_font.render(initial, True, WHITE)
            initial_pos = (
                self.portrait_rect.centerx - initial_surf.get_width() // 2,
                self.portrait_rect.centery - initial_surf.get_height() // 2
            )
            screen.blit(initial_surf, initial_pos)
        
        # Draw NPC name
        name_text = self.font.render(self.npc_name, True, WHITE)
        name_pos = (
            self.portrait_rect.centerx - name_text.get_width() // 2,
            self.portrait_rect.bottom + 5
        )
        screen.blit(name_text, name_pos)
        
        # Draw divider between portrait and text
        pygame.draw.line(
            screen, WHITE,
            (self.portrait_rect.right + 10, self.portrait_rect.top),
            (self.portrait_rect.right + 10, self.portrait_rect.bottom),
            2
        )
        
        # Draw dialogue text with word wrap
        self._draw_wrapped_text(screen, self.dialog_text, self.text_rect, self.font, WHITE)
        
        # Draw divider above options
        pygame.draw.line(
            screen, WHITE,
            (self.options_rect.left, self.options_rect.top - 10),
            (self.options_rect.right, self.options_rect.top - 10),
            1
        )
        
        # Draw dialogue options
        self.option_buttons = []  # Reset buttons
        y_pos = self.options_rect.y + 10
        
        for i, option in enumerate(self.options):
            if 'text' in option:
                # Create option button
                btn_height = 40
                btn_rect = pygame.Rect(
                    self.options_rect.x + 20,
                    y_pos,
                    self.options_rect.width - 40,
                    btn_height
                )
                
                # Draw button
                pygame.draw.rect(screen, DARK_GREY, btn_rect)
                pygame.draw.rect(screen, SILVER, btn_rect, 1)
                
                # Draw option number
                num_text = self.font.render(f"{i+1}.", True, YELLOW)
                screen.blit(num_text, (btn_rect.x + 10, btn_rect.y + (btn_height - num_text.get_height()) // 2))
                
                # Draw option text
                option_text = self.font.render(option['text'], True, WHITE)
                screen.blit(option_text, (
                    btn_rect.x + 40,
                    btn_rect.y + (btn_height - option_text.get_height()) // 2
                ))
                
                # Store button for click detection
                self.option_buttons.append((btn_rect, i))
                
                y_pos += btn_height + 10
    
    def _draw_wrapped_text(self, screen, text, rect, font, color):
        """Draw text wrapped to fit inside a rectangle"""
        words = text.split()
        line = ""
        y_offset = rect.y
        
        for word in words:
            test_line = line + word + " "
            test_surf = font.render(test_line, True, color)
            
            if test_surf.get_width() < rect.width:
                line = test_line
            else:
                # Draw current line
                if line:
                    text_surf = font.render(line, True, color)
                    screen.blit(text_surf, (rect.x, y_offset))
                    y_offset += font.get_linesize()
                    
                # Start new line with current word
                line = word + " "
                
                # Check if we've run out of space
                if y_offset > rect.bottom - font.get_linesize():
                    # Draw ellipsis and exit
                    screen.blit(font.render("...", True, color), (rect.x, y_offset))
                    return
        
        # Draw the last line
        if line:
            text_surf = font.render(line, True, color)
            screen.blit(text_surf, (rect.x, y_offset))
    
    def handle_click(self, pos):
        # Check for close button
        result = super().handle_click(pos)
        if result:
            return result
        
        # Check for option buttons
        for btn_rect, option_index in self.option_buttons:
            if btn_rect.collidepoint(pos):
                return {"action": "select_option", "index": option_index}
        
        return None