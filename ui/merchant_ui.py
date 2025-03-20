import pygame
from game_config import *
from ui.base_ui import BaseUI
from components.items import MERCHANT_ITEMS

class MerchantUI(BaseUI):
    def __init__(self, player):
        # Larger UI for merchant screen
        super().__init__(1/8, 1/8, 3/4, 3/4, title="Trading Post")
        self.player = player
        
        # Split UI into buy and sell sections
        self.buy_rect = pygame.Rect(self.bg_rect.x + 20, self.bg_rect.y + 50,
                                 self.bg_rect.width // 2 - 30, self.bg_rect.height - 80)
        
        self.sell_rect = pygame.Rect(self.bg_rect.x + self.bg_rect.width // 2 + 10, self.bg_rect.y + 50,
                                   self.bg_rect.width // 2 - 30, self.bg_rect.height - 80)
        
        # Item buttons
        self.buy_buttons = []
        self.sell_buttons = []
        
        # Initialize buy and sell items
        self.update_buy_buttons()
        self.update_sell_buttons()
    
    def update_buy_buttons(self):
        """Update the buy section with merchant items"""
        self.buy_buttons = []
        
        for i, item in enumerate(MERCHANT_ITEMS):
            button_rect = pygame.Rect(self.buy_rect.x + 10, self.buy_rect.y + 40 + i * 50, 
                                    self.buy_rect.width - 20, 40)
            self.buy_buttons.append({
                "item": item,
                "rect": button_rect
            })
            # Add to clickable elements
            self.add_clickable(f"buy_{i}", button_rect)
    
    def update_sell_buttons(self):
        """Update the sell section with player inventory items"""
        self.sell_buttons = []
        
        # Clear old sell clickables
        sell_keys = [k for k in self.clickable_elements.keys() if k.startswith("sell_")]
        for key in sell_keys:
            self.remove_clickable(key)
        
        # Collect all unique items from player inventory
        sell_items = []
        item_counts = {}
        
        for row in self.player.inventory:
            for slot in row:
                if slot["item"]:
                    item_name = slot["item"].name
                    if item_name not in item_counts:
                        sell_items.append(slot["item"])
                        item_counts[item_name] = slot["count"]
                    else:
                        item_counts[item_name] += slot["count"]
        
        # Create buttons for each item type
        for i, item in enumerate(sell_items):
            button_rect = pygame.Rect(self.sell_rect.x + 10, self.sell_rect.y + 40 + i * 50, 
                                    self.sell_rect.width - 20, 40)
            self.sell_buttons.append({
                "item": item,
                "count": item_counts[item.name],
                "rect": button_rect
            })
            # Add to clickable elements
            self.add_clickable(f"sell_{i}", button_rect)
    
    def update(self):
        super().update()
        
        mouse_pos = pygame.mouse.get_pos()
        
        # Reset hover state
        self.hover_item = None
        
        # Check for hovering over buy items
        for button in self.buy_buttons:
            if button["rect"].collidepoint(mouse_pos):
                self.hover_item = button["item"]
                break
        
        # Check for hovering over sell items
        for button in self.sell_buttons:
            if button["rect"].collidepoint(mouse_pos):
                self.hover_item = button["item"]
                break
        
        # Update sell buttons to reflect current inventory
        self.update_sell_buttons()
    
    def draw(self, screen):
        # Draw base UI
        super().draw(screen)
        
        # Draw silver amount
        silver_text = self.font.render(f"Silver: {self.player.stats.silver}", True, SILVER)
        screen.blit(silver_text, (self.bg_rect.x + 20, self.bg_rect.top + 15))
        
        # Draw buy section
        pygame.draw.rect(screen, GREY, self.buy_rect)
        pygame.draw.rect(screen, WHITE, self.buy_rect, 1)
        
        buy_title = self.font.render("Buy Items", True, WHITE)
        screen.blit(buy_title, (self.buy_rect.centerx - buy_title.get_width() // 2, 
                              self.buy_rect.y + 10))
        
        # Draw buy buttons
        for button in self.buy_buttons:
            item = button["item"]
            rect = button["rect"]
            
            # Button background
            can_afford = self.player.stats.silver >= item.value
            button_color = GREEN if can_afford else RED
            
            pygame.draw.rect(screen, button_color, rect, 0, 5)
            pygame.draw.rect(screen, WHITE, rect, 1, 5)
            
            # Item image
            item_img = item.get_image(30)
            screen.blit(item_img, (rect.x + 5, rect.y + 5))
            
            # Item name and price
            name_text = self.small_font.render(item.name, True, WHITE)
            price_text = self.small_font.render(f"{item.value} silver", True, SILVER)
            
            screen.blit(name_text, (rect.x + 40, rect.y + 5))
            screen.blit(price_text, (rect.x + 40, rect.y + 22))
        
        # Draw sell section
        pygame.draw.rect(screen, GREY, self.sell_rect)
        pygame.draw.rect(screen, WHITE, self.sell_rect, 1)
        
        sell_title = self.font.render("Sell Items", True, WHITE)
        screen.blit(sell_title, (self.sell_rect.centerx - sell_title.get_width() // 2, 
                              self.sell_rect.y + 10))
        
        # Draw sell buttons
        for button in self.sell_buttons:
            item = button["item"]
            rect = button["rect"]
            count = button["count"]
            
            # Button background
            pygame.draw.rect(screen, BLUE, rect, 0, 5)
            pygame.draw.rect(screen, WHITE, rect, 1, 5)
            
            # Item image
            item_img = item.get_image(30)
            screen.blit(item_img, (rect.x + 5, rect.y + 5))
            
            # Item name, count and value
            name_text = self.small_font.render(item.name, True, WHITE)
            count_text = self.small_font.render(f"x{count}", True, WHITE)
            value_text = self.small_font.render(f"+{item.value} silver each", True, SILVER)
            
            screen.blit(name_text, (rect.x + 40, rect.y + 5))
            screen.blit(count_text, (rect.right - count_text.get_width() - 10, rect.y + 5))
            screen.blit(value_text, (rect.x + 40, rect.y + 22))
        
        # Draw tooltip if hovering over an item
        if self.hover_item:
            mouse_pos = pygame.mouse.get_pos()
            tooltip_text = f"{self.hover_item.name}\n{self.hover_item.description}"
            self.draw_tooltip(screen, tooltip_text, mouse_pos)
    
    def handle_click(self, pos):
        # Check if close button clicked
        result = super().handle_click(pos)
        if result == "close":
            return "close"
        
        # Check buy buttons
        for i, button in enumerate(self.buy_buttons):
            if button["rect"].collidepoint(pos):
                self.buy_item(button["item"])
                return None
        
        # Check sell buttons
        for i, button in enumerate(self.sell_buttons):
            if button["rect"].collidepoint(pos):
                self.sell_item(button["item"])
                return None
                
        return None
    
    def buy_item(self, item):
        """Buy an item from the merchant"""
        if self.player.stats.silver >= item.value:
            if self.player.add_ore(item):  # Add item to inventory
                self.player.stats.silver -= item.value
            else:
                print("Inventory full!")
        else:
            print("Not enough silver!")
    
    def sell_item(self, item):
        """Sell an item to the merchant"""
        # Find the item in player inventory
        for row in range(INVENTORY_ROWS):
            for col in range(INVENTORY_COLS):
                slot = self.player.inventory[row][col]
                if slot["item"] and slot["item"].name == item.name:
                    # Remove one item and add value to silver
                    slot["count"] -= 1
                    self.player.stats.silver += item.value
                    
                    # If stack is empty, remove item type
                    if slot["count"] <= 0:
                        slot["item"] = None
                        slot["count"] = 0
                    
                    self.player.total_ore -= 1
                    
                    # Update sell buttons after selling
                    self.update_sell_buttons()
                    return