import pygame
from game_config import *
from ui.base_ui import BaseUI

class InventoryUI(BaseUI):
    def __init__(self, player):
        super().__init__()
        self.player = player
        
        # Calculate grid properties
        self.grid_margin = 10
        self.grid_top = self.bg_rect.top + 50
        self.cell_size = 50
        self.cell_margin = 5
        
        # Calculate grid dimensions
        grid_width = INVENTORY_COLS * (self.cell_size + self.cell_margin) - self.cell_margin
        grid_height = INVENTORY_ROWS * (self.cell_size + self.cell_margin) - self.cell_margin
        
        # Center the grid
        self.grid_left = self.bg_rect.centerx - grid_width // 2
        
        # Tooltip
        self.hover_cell = None
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if hovering over an inventory cell
        self.hover_cell = None
        
        # Loop through grid cells
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                cell_rect = self.get_cell_rect(row, col)
                
                # Check if mouse is over non-empty cell
                if cell_rect.collidepoint(mouse_pos) and self.player.inventory[row][col]["item"] is not None:
                    self.hover_cell = (row, col)
                    break
    
    def get_cell_rect(self, row, col):
        """Get rectangle for specific inventory cell"""
        x = self.grid_left + col * (self.cell_size + self.cell_margin)
        y = self.grid_top + row * (self.cell_size + self.cell_margin)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)
    
    def draw(self, screen):
        # Draw base UI elements
        super().draw(screen)
        
        # Draw title
        self.draw_title(screen, "Inventory")
        
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
            
            mouse_pos = pygame.mouse.get_pos()
            tooltip_text = f"{item.name} ({count})\nValue: {item.value} silver each\n{item.description}"
            self.draw_tooltip(screen, tooltip_text, mouse_pos)