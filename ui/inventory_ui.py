import pygame
from game_config import *

class InventoryUI:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        
        # Inventory background
        self.bg_rect = pygame.Rect(SCREEN_WIDTH // 6, SCREEN_HEIGHT // 6, 
                                   SCREEN_WIDTH * 2 // 3, SCREEN_HEIGHT * 2 // 3)
        
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
        self.hover_cell = None
        self.tooltip_bg = pygame.Surface((120, 30))
        self.tooltip_bg.set_alpha(200)
        self.tooltip_bg.fill((30, 30, 30))
        
        # Calculate grid cell size and spacing
        self.grid_margin = 10
        self.grid_top = self.bg_rect.top + 50
        self.cell_size = 50
        self.cell_margin = 5
        
        # Calculate total grid width and height
        grid_width = INVENTORY_COLS * (self.cell_size + self.cell_margin) - self.cell_margin
        grid_height = INVENTORY_ROWS * (self.cell_size + self.cell_margin) - self.cell_margin
        
        # Center the grid
        self.grid_left = self.bg_rect.centerx - grid_width // 2
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if hovering over an inventory cell
        self.hover_cell = None
        
        # Loop through each grid cell
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                cell_rect = self.get_cell_rect(row, col)
                
                # Check if mouse is over cell with content
                if cell_rect.collidepoint(mouse_pos) and self.player.inventory[row][col]["item"] is not None:
                    self.hover_cell = (row, col)
                    break
    
    def get_cell_rect(self, row, col):
        """Get the rectangle for a specific inventory cell"""
        x = self.grid_left + col * (self.cell_size + self.cell_margin)
        y = self.grid_top + row * (self.cell_size + self.cell_margin)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)
    
    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, DARK_GREY, self.bg_rect)
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
        
        # Draw title
        title = self.font.render("Inventory", True, WHITE)
        screen.blit(title, (self.bg_rect.centerx - title.get_width() // 2, self.bg_rect.top + 15))
        
        # Draw close button
        screen.blit(self.close_img, self.close_rect)
        
        # Draw silver amount
        silver_text = self.font.render(f"Silver: {self.player.stats.silver}", True, SILVER)
        screen.blit(silver_text, (self.bg_rect.x + 20, self.bg_rect.top + 15))
        
        # Draw inventory grid
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                # Draw cell background
                cell_rect = self.get_cell_rect(row, col)
                pygame.draw.rect(screen, GREY, cell_rect)
                
                # Draw item if cell has content
                slot = self.player.inventory[row][col]
                if slot["item"] is not None:
                    # Draw item image
                    item_img = slot["item"].get_image(self.cell_size)
                    screen.blit(item_img, cell_rect.topleft)
                    
                    # Draw count
                    count_text = self.small_font.render(str(slot["count"]), True, WHITE)
                    screen.blit(count_text, (cell_rect.right - count_text.get_width() - 2, 
                                             cell_rect.bottom - count_text.get_height() - 2))
        
        # Draw total
        total_text = self.font.render(f"Total: {self.player.total_ore}", True, WHITE)
        screen.blit(total_text, (self.bg_rect.centerx - total_text.get_width() // 2, 
                                self.bg_rect.bottom - 40))
        
        # Draw tooltip if hovering over an item
        if self.hover_cell:
            row, col = self.hover_cell
            item = self.player.inventory[row][col]["item"]
            count = self.player.inventory[row][col]["count"]
            
            # Create tooltip text
            name_line = f"{item.name} ({count})"
            value_line = f"Value: {item.value} silver each"
            
            tooltip_height = 55  # Height for two lines
            tooltip_width = max(
                self.font.size(name_line)[0],
                self.small_font.size(value_line)[0],
                self.small_font.size(item.description)[0]
            ) + 20
            
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw tooltip background
            tooltip_rect = pygame.Rect(mouse_pos[0] + 10, mouse_pos[1] + 10, tooltip_width, tooltip_height)
            tooltip_bg = pygame.Surface((tooltip_rect.width, tooltip_rect.height))
            tooltip_bg.set_alpha(200)
            tooltip_bg.fill((30, 30, 30))
            
            # Make sure tooltip doesn't go off screen
            if tooltip_rect.right > SCREEN_WIDTH:
                tooltip_rect.right = SCREEN_WIDTH - 5
            if tooltip_rect.bottom > SCREEN_HEIGHT:
                tooltip_rect.bottom = SCREEN_HEIGHT - 5
            
            screen.blit(tooltip_bg, tooltip_rect)
            
            # Draw tooltip text
            name_text = self.font.render(name_line, True, WHITE)
            value_text = self.small_font.render(value_line, True, SILVER)
            screen.blit(name_text, (tooltip_rect.x + 10, tooltip_rect.y + 10))
            screen.blit(value_text, (tooltip_rect.x + 10, tooltip_rect.y + 35))
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"  # Signal main.py to close inventory
        return False