import pygame
from game_config import *
from ui.base_ui import BaseUI

class HangarUI(BaseUI):
    def __init__(self, player):
        super().__init__()
        self.player = player
        
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
        self.draw_background(screen)
        
        # Draw title
        self.draw_title(screen, "Drone Bay")
        
        # Draw close button
        self.draw_close_button(screen)
        
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
            
            tooltip_text = "Empty Drone Slot"
            if self.drone_slots[self.hover_cell]["type"]:
                tooltip_text = f"Drone: {self.drone_slots[self.hover_cell]['type']}"
            
            self.draw_tooltip(screen, tooltip_text, mouse_pos)
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"
        
        # Check if a drone slot was clicked
        if self.hover_cell is not None:
            # Will handle drone activation/deactivation later
            pass
        
        return False