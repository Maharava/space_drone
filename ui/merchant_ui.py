import pygame
from game_config import *
from components.items import MERCHANT_ITEMS, ORE_TYPES

class MerchantUI:
    def __init__(self, player):
        self.player = player
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 18)
        self.title_font = pygame.font.SysFont(None, 30)
        
        # Merchant background
        self.bg_rect = pygame.Rect(SCREEN_WIDTH // 8, SCREEN_HEIGHT // 8, 
                                   SCREEN_WIDTH * 3 // 4, SCREEN_HEIGHT * 3 // 4)
        
        # Close button
        try:
            self.close_img = pygame.image.load("assets/close.png").convert_alpha()
            self.close_img = pygame.transform.scale(self.close_img, (20, 20))
        except:
            self.close_img = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.line(self.close_img, RED, (0, 0), (20, 20), 3)
            pygame.draw.line(self.close_img, RED, (0, 20), (20, 0), 3)
        
        self.close_rect = self.close_img.get_rect(topright=(self.bg_rect.right - 10, self.bg_rect.top + 10))
        
        # Split the UI into buy and sell sections
        self.buy_rect = pygame.Rect(self.bg_rect.x + 20, self.bg_rect.y + 50,
                                 self.bg_rect.width // 2 - 30, self.bg_rect.height - 80)
        
        self.sell_rect = pygame.Rect(self.bg_rect.x + self.bg_rect.width // 2 + 10, self.bg_rect.y + 50,
                                   self.bg_rect.width // 2 - 30, self.bg_rect.height - 80)
        
        # Item buttons
        self.buy_buttons = []
        self.sell_buttons = []
        
        # Tooltip
        self.hover_item = None
        
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
    
    def update_sell_buttons(self):
        """Update the sell section with player inventory items"""
        self.sell_buttons = []
        
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
    
    def update(self):
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
        # Draw background
        pygame.draw.rect(screen, DARK_GREY, self.bg_rect)
        pygame.draw.rect(screen, WHITE, self.bg_rect, 2)
        
        # Draw title
        title = self.title_font.render("Trading Post", True, WHITE)
        screen.blit(title, (self.bg_rect.centerx - title.get_width() // 2, self.bg_rect.top + 15))
        
        # Draw close button
        screen.blit(self.close_img, self.close_rect)
        
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
            
            tooltip_bg = pygame.Surface((300, 60))
            tooltip_bg.set_alpha(200)
            tooltip_bg.fill((30, 30, 30))
            
            tooltip_rect = tooltip_bg.get_rect(topleft=(mouse_pos[0] + 10, mouse_pos[1] + 10))
            
            # Make sure tooltip doesn't go off screen
            if tooltip_rect.right > SCREEN_WIDTH:
                tooltip_rect.right = SCREEN_WIDTH - 5
            if tooltip_rect.bottom > SCREEN_HEIGHT:
                tooltip_rect.bottom = SCREEN_HEIGHT - 5
                
            screen.blit(tooltip_bg, tooltip_rect)
            
            # Item name and description with word wrap
            name_text = self.font.render(self.hover_item.name, True, WHITE)
            screen.blit(name_text, (tooltip_rect.x + 10, tooltip_rect.y + 10))
            
            desc_text = self.small_font.render(self.hover_item.description, True, SILVER)
            
            # Word wrap for description
            words = self.hover_item.description.split()
            line = ""
            y_pos = tooltip_rect.y + 35
            
            for word in words:
                test_line = line + word + " "
                test_width = self.small_font.size(test_line)[0]
                
                if test_width < tooltip_rect.width - 20:
                    line = test_line
                else:
                    text = self.small_font.render(line, True, SILVER)
                    screen.blit(text, (tooltip_rect.x + 10, y_pos))
                    y_pos += 20
                    line = word + " "
            
            if line:
                text = self.small_font.render(line, True, SILVER)
                screen.blit(text, (tooltip_rect.x + 10, y_pos))
    
    def handle_click(self, pos):
        # Check if close button clicked
        if self.close_rect.collidepoint(pos):
            return "close"
        
        # Check buy buttons
        for button in self.buy_buttons:
            if button["rect"].collidepoint(pos):
                item = button["item"]
                # Try to buy the item
                if self.player.stats.silver >= item.value:
                    if self.player.add_ore(item):  # Add item to inventory
                        self.player.stats.silver -= item.value
                        print(f"Bought {item.name} for {item.value} silver")
                    else:
                        print("Inventory full!")
                else:
                    print("Not enough silver!")
                return None
        
        # Check sell buttons
        for button in self.sell_buttons:
            if button["rect"].collidepoint(pos):
                item = button["item"]
                # Find the item in player inventory
                for row in range(INVENTORY_ROWS):
                    for col in range(INVENTORY_COLS):
                        slot = self.player.inventory[row][col]
                        if slot["item"] and slot["item"].name == item.name:
                            # Remove one item and add value to silver
                            slot["count"] -= 1
                            self.player.stats.silver += item.value
                            print(f"Sold {item.name} for {item.value} silver")
                            
                            # If stack is empty, remove item type
                            if slot["count"] <= 0:
                                slot["item"] = None
                                slot["count"] = 0
                            
                            self.player.total_ore -= 1
                            return None
                            
        return None