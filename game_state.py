import pygame
from game_config import *
from components.asteroid import Asteroid  # Import the Asteroid class directly

class GameState:
    """Base game state class"""
    def __init__(self, game):
        self.game = game  # Reference to main game object
    
    def update(self):
        """Update game logic for this state"""
        pass
    
    def draw(self, screen):
        """Draw this state to the screen"""
        pass
    
    def handle_event(self, event):
        """Handle a pygame event"""
        pass
    
    def enter(self):
        """Called when entering this state"""
        pass
    
    def exit(self):
        """Called when exiting this state"""
        pass

class RunningState(GameState):
    """Main gameplay state"""
    def update(self):
        # Update all sprites
        self.game.all_sprites.update(0)  # 0 = GAME_RUNNING in old system
        
        # Update camera
        self.game.camera.update(self.game.player)
        
        # Update UI elements
        self.game.jump_ui.update(self.game.player.position)
        
        # Check for station interactions
        station = self.game.map_system.get_nearest_station(self.game.player.position)
        can_interact = station and station.can_interact(self.game.player.position)
        self.game.interact_ui.update(can_interact, station.name if can_interact else None)
        
        # Handle asteroid respawning - using the class method directly
        Asteroid.update_respawns(self.game.all_sprites, self.game.asteroids)
        
        # Handle collision detection
        self.game.handle_collision_detection()
    
    def draw(self, screen):
        # Clear screen
        screen.fill(BLACK)
        
        # Draw sprites with camera offset
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw UI elements
        self.game.jump_ui.draw(screen)
        self.game.interact_ui.draw(screen)
        
        # Draw HUD
        self.game.draw_hud()
        self.game.draw_fps()
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.game.change_state("inventory")
            elif event.key == pygame.K_h:
                self.game.change_state("hangar")
            elif event.key == pygame.K_e:
                # Try to interact with nearest station
                station = self.game.map_system.get_nearest_station(self.game.player.position)
                if station and station.can_interact(self.game.player.position):
                    self.game.conversation_ui.set_dialog(station.name, station.dialog)
                    self.game.change_state("conversation")
            elif event.key == pygame.K_SPACE:
                # Check for jump
                if self.game.jump_ui.visible:
                    self.game.handle_jump()

class InventoryState(GameState):
    """Inventory UI state"""
    def enter(self):
        self.game.inventory_ui.update()
    
    def update(self):
        self.game.inventory_ui.update()
    
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw inventory UI
        self.game.inventory_ui.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("running")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.inventory_ui.handle_click(event.pos)
            if result == "close":
                self.game.change_state("running")

class HangarState(GameState):
    """Hangar UI state"""
    def enter(self):
        self.game.hangar_ui.update()
    
    def update(self):
        self.game.hangar_ui.update()
    
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw hangar UI
        self.game.hangar_ui.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("running")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.hangar_ui.handle_click(event.pos)
            if result == "close":
                self.game.change_state("running")

class ConversationState(GameState):
    """Conversation UI state"""
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            if sprite != self.game.player:  # Don't update player during conversation
                screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw conversation UI
        self.game.conversation_ui.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.conversation_ui.handle_click(event.pos)
            if result == "close":
                self.game.change_state("running")
            elif result == "barter":
                self.game.change_state("merchant")

class MerchantState(GameState):
    """Merchant UI state"""
    def enter(self):
        self.game.merchant_ui.update()
    
    def update(self):
        self.game.merchant_ui.update()
    
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw merchant UI
        self.game.merchant_ui.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.merchant_ui.handle_click(event.pos)
            if result == "close":
                self.game.change_state("running")