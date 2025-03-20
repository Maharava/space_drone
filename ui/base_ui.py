import pygame
from game_config import *
from utils import load_image

class BaseUI:
    """Base class for all UI panels"""
    def __init__(self, x_fraction=1/6, y_fraction=1/6, width_fraction=2/3, height_fraction=2/3, title=None):
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
        
        # UI title
        self.title = title
        
        # Close button
        self.close_img = load_image("close", size=20, fallback_color=RED)
        self.close_rect = self.close_img.get_rect(topright=(self.bg_rect.right - 10, self.bg_rect.top + 10))
        
        # Hover item tracking
        self.hover_item = None
        
        # Clickable elements for easier interaction handling
        self.clickable_elements = {
            "close": self.close_rect  # Add the close button by default
        }
    
    def update(self):
        """Update UI state - track mouse for hover effects"""
        mouse_pos = pygame.mouse.get_pos()
        self.hover_item = None
        
        # Subclasses should override this to check specific hover areas
        # but can call super().update() to get this base behavior
    
    def draw_background(self, screen):
        """Draw the standard UI background panel"""
        # Draw background panel
        pygame.draw.rect(screen, DARK_GREY, self.bg_rect)
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
    
    def draw_title(self, screen, title_text=None):
        """Draw the UI title"""
        # Use provided title or instance title
        title_text = title_text or self.title
        if not title_text:
            return
            
        # Draw title text
        title = self.title_font.render(title_text, True, WHITE)
        screen.blit(title, (self.bg_rect.centerx - title.get_width() // 2, self.bg_rect.top + 15))
    
    def draw_close_button(self, screen):
        """Draw the close button"""
        screen.blit(self.close_img, self.close_rect)
    
    def draw(self, screen):
        """Base draw method - draws background and close button"""
        self.draw_background(screen)
        self.draw_close_button(screen)
        
        # Draw title if set
        if self.title:
            self.draw_title(screen)
    
    def handle_click(self, pos):
        """Handle click events on UI elements
        Returns:
            str or None: Action identifier or None if no action
        """
        # Check standard clickable elements
        for action, rect in self.clickable_elements.items():
            if rect.collidepoint(pos):
                return action
                
        # No action found
        return None
    
    def add_clickable(self, name, rect):
        """Add a named clickable element"""
        self.clickable_elements[name] = rect
    
    def remove_clickable(self, name):
        """Remove a named clickable element"""
        if name in self.clickable_elements:
            del self.clickable_elements[name]
    
    def draw_tooltip(self, screen, text, mouse_pos):
        """Draw a tooltip with text at the given position"""
        # Create tooltip background
        lines = text.split('\n')
        
        # Calculate size based on text
        line_height = 20
        max_width = max([self.small_font.size(line)[0] for line in lines]) + 20
        height = len(lines) * line_height + 10
        
        tooltip_bg = pygame.Surface((max_width, height))
        tooltip_bg.set_alpha(220)
        tooltip_bg.fill((30, 30, 30))
        
        tooltip_rect = tooltip_bg.get_rect(topleft=(mouse_pos[0] + 10, mouse_pos[1] + 10))
        
        # Make sure tooltip doesn't go off screen
        if tooltip_rect.right > SCREEN_WIDTH:
            tooltip_rect.right = SCREEN_WIDTH - 5
        if tooltip_rect.bottom > SCREEN_HEIGHT:
            tooltip_rect.bottom = SCREEN_HEIGHT - 5
            
        screen.blit(tooltip_bg, tooltip_rect)
        
        # Draw text lines
        for i, line in enumerate(lines):
            text_surf = self.small_font.render(line, True, SILVER)
            screen.blit(text_surf, (tooltip_rect.x + 10, tooltip_rect.y + 5 + i * line_height))
    
    def draw_grid(self, screen, left, top, cols, rows, cell_size, cell_margin=5):
        """Helper to draw a grid of cells
        Returns:
            list: List of cell rects in row-major order
        """
        cells = []
        for row in range(rows):
            for col in range(cols):
                x = left + col * (cell_size + cell_margin)
                y = top + row * (cell_size + cell_margin)
                cell_rect = pygame.Rect(x, y, cell_size, cell_size)
                cells.append(cell_rect)
                pygame.draw.rect(screen, GREY, cell_rect)
        return cells