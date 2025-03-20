import pygame
from game_config import *

class HangarUI:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        
        # Hangar background
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
        
        # Hangar grid for drones
        self.grid_margin = 10
        self.grid_top = self.bg_rect.top + 50
        self.cell_size = 60
        self.cell_margin = 10
        
        # Define drone grid size
        self.drone_cols = 4
        self.drone_rows = 3
        
        # Calculate total grid width and height
        grid_width = self.drone_cols * (self.cell_size + self.cell_margin) - self.cell_margin
        grid_height = self.drone_rows * (self.cell_size + self.cell_margin) - self.cell_margin
        
        # Center the grid
        self.grid_left = self.bg_rect.centerx - grid_width // 2
        
        # Placeholder for drone slots
        self.drone_slots = []
        for row in range(self.drone_rows):
            for col in range(self.drone_cols):
                self.drone_slots.append({"active": False, "type": None})
        
        # Tooltip
        self.hover_cell = None
    
    def update(self):
        mouse_pos = pygame.mouse.get_pos()
        
        # Check if hovering over a drone slot
        self.hover_cell = None
        
        for i in range(len(self.drone_slots)):
            cell_rect = self.get_cell_rect(i)
            if cell_rect.collidepoint(mouse_pos):
                self.hover_cell = i
                break
    
    def get_cell_rect(self, index):
        """Get rectangle for a specific drone slot"""
        row = index // self.drone_cols
        col = index % self.drone_cols
        
        x = self.grid_left + col * (self.cell_size + self.cell_margin)
        y = self.grid_top + row * (self.cell_size + self.cell_margin)
        return pygame.Rect(x, y, self.cell_size, self.cell_size)
    
    def draw(self, screen):
        # Draw background
        pygame.draw.rect(screen, DARK_GREY, self.bg_rect)
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
        
        # Draw title
        title = self.font.render("Drone Bay", True, WHITE)
        screen.blit(title, (self.bg_rect.centerx - title.get_width() // 2, self.bg_rect.top + 15))
        
        # Draw close button
        screen.blit(self.close_img, self.close_rect)
        
        # Draw drone slots
        for i, slot in enumerate(self.drone_slots):
            cell_rect = self.get_cell_rect(i)
            
            # Draw cell background
            cell_color = GREY
            if slot["active"]:
                cell_color = (70, 70, 120)  # Darker blue for active drones
            
            pygame.draw.rect(screen, cell_color, cell_rect)
            pygame.draw.rect(screen, WHITE, cell_rect, 1)
            
            # If drone exists in slot, draw it
            if slot["type"]:
                slot_text = self.small_font.render(slot["type"], True, WHITE)
                screen.blit(slot_text, (cell_rect.centerx - slot_text.get_width() // 2, 
                                       cell_rect.centery - slot_text.get_height() // 2))
        
        # Draw info text at bottom
        info_text = self.small_font.render("Drone slots: 0 / " + str(self.player.hangar.get_capacity()), True, WHITE)
        screen.blit(info_text, (self.bg_rect.centerx - info_text.get_width() // 2, 
                               self.bg_rect.bottom - 30))
        
        # Draw tooltip if hovering over a slot
        if self.hover_cell is not None:
            mouse_pos = pygame.mouse.get_pos()
            
            tooltip_bg = pygame.Surface((150, 30))
            tooltip_bg.set_alpha(200)
            tooltip_bg.fill((30, 30, 30))
            
            tooltip_text = "Empty Drone Slot"
            if self.drone_slots[self.hover_cell]["type"]:
                tooltip_text = f"Drone: {self.drone_slots[self.hover_cell]['type']}"
            
            tooltip = self.small_font.render(tooltip_text, True, WHITE)
            tooltip_rect = tooltip_bg.get_rect(topleft=(mouse_pos[0] + 10, mouse_pos[1] + 10))
            tooltip_rect.width = tooltip.get_width() + 10
            
            screen.blit(tooltip_bg, tooltip_rect)
            screen.blit(tooltip, (mouse_pos[0] + 15, mouse_pos[1] + 15))
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"
        
        # Check if a drone slot was clicked
        if self.hover_cell is not None:
            # Will handle drone activation/deactivation later
            pass
        
        return False