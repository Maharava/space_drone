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
        
        # Ore images
        self.ore_imgs = {}
        
        # Low-grade ore (brown)
        try:
            self.ore_imgs["low-grade"] = pygame.image.load("assets/low_grade_ore.png").convert_alpha()
        except:
            self.ore_imgs["low-grade"] = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.ore_imgs["low-grade"], BROWN, (20, 20), 20)
        
        # High-grade ore (yellow)
        try:
            self.ore_imgs["high-grade"] = pygame.image.load("assets/high_grade_ore.png").convert_alpha()
        except:
            self.ore_imgs["high-grade"] = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.ore_imgs["high-grade"], YELLOW, (20, 20), 20)
        
        # Rare ore (purple)
        try:
            self.ore_imgs["rare-ore"] = pygame.image.load("assets/rare_ore.png").convert_alpha()
        except:
            self.ore_imgs["rare-ore"] = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.ore_imgs["rare-ore"], PURPLE, (20, 20), 20)
        
        # Silver ore (silver)
        try:
            self.ore_imgs["silver"] = pygame.image.load("assets/silver_ore.png").convert_alpha()
        except:
            self.ore_imgs["silver"] = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.ore_imgs["silver"], SILVER, (20, 20), 20)
        
        # Resize all ore images
        for key in self.ore_imgs:
            self.ore_imgs[key] = pygame.transform.scale(self.ore_imgs[key], (40, 40))
        
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
                if cell_rect.collidepoint(mouse_pos) and self.player.inventory[row][col]["type"] is not None:
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
        
        # Draw inventory grid
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                # Draw cell background
                cell_rect = self.get_cell_rect(row, col)
                pygame.draw.rect(screen, GREY, cell_rect)
                
                # Draw item if cell has content
                slot = self.player.inventory[row][col]
                if slot["type"] is not None:
                    # Draw ore image
                    ore_img = self.ore_imgs[slot["type"]]
                    screen.blit(ore_img, cell_rect.topleft)
                    
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
            ore_type = self.player.inventory[row][col]["type"]
            count = self.player.inventory[row][col]["count"]
            
            tooltip = self.font.render(f"{ore_type} ({count})", True, WHITE)
            mouse_pos = pygame.mouse.get_pos()
            
            # Draw tooltip background
            tooltip_rect = self.tooltip_bg.get_rect(topleft=(mouse_pos[0] + 10, mouse_pos[1] + 10))
            tooltip_rect.width = tooltip.get_width() + 10
            tooltip_bg = pygame.Surface((tooltip_rect.width, tooltip_rect.height))
            tooltip_bg.set_alpha(200)
            tooltip_bg.fill((30, 30, 30))
            
            screen.blit(tooltip_bg, tooltip_rect)
            screen.blit(tooltip, (mouse_pos[0] + 15, mouse_pos[1] + 15))
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            global game_state
            from main import GAME_RUNNING
            game_state = GAME_RUNNING
            return True
        return False