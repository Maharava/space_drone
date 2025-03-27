import pygame
from game_config import *
from components.asteroid import Asteroid

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
        
        # Handle asteroid respawning
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
                    if hasattr(self.game, 'quest_manager'):
                        # Use quest system dialogue if available
                        if self.game.quest_manager.start_station_dialogue(station):
                            text = self.game.quest_manager.get_current_text()
                            options = self.game.quest_manager.get_current_options()
                            self.game.conversation_ui.set_dialog(station.name, text, options)
                        else:
                            # Fallback to basic dialogue
                            self.game.conversation_ui.set_dialog(station.name, station.dialog)
                    else:
                        # Use regular dialogue without quest system
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
    """Station conversation UI state"""
    def enter(self):
        # Start dialogue with nearest station
        station = self.game.map_system.get_nearest_station(self.game.player.position)
        if station:
            # Try to start quest dialogue if available
            if hasattr(self.game, 'quest_manager'):
                if self.game.quest_manager.start_station_dialogue(station):
                    text = self.game.quest_manager.get_current_text()
                    options = self.game.quest_manager.get_current_options()
                    
                    # Update UI with dialogue options
                    self.game.conversation_ui.set_dialog(station.name, text, options)
                else:
                    # Fallback to basic dialogue
                    self.game.conversation_ui.set_dialog(station.name, station.dialog)
            else:
                # Use regular dialogue without quest system
                self.game.conversation_ui.set_dialog(station.name, station.dialog)
    
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
            elif result == "jobs":
                self.game.change_state("jobs")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("running")
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                # Handle dialogue option selection
                if hasattr(self.game, 'quest_manager'):
                    option_index = event.key - pygame.K_1
                    options = self.game.quest_manager.get_current_options()
                    if option_index < len(options):
                        # Select the option
                        result = self.game.quest_manager.select_option(option_index)
                        
                        # Update the UI
                        text = self.game.quest_manager.get_current_text()
                        options = self.game.quest_manager.get_current_options()
                        
                        if text:
                            # Get speaker name
                            speaker = self.game.conversation_ui.speaker
                            if self.game.quest_manager.current_npc:
                                # NPC conversation started, switch to NPC dialogue UI
                                npc_name = self.game.quest_manager.current_npc.name
                                self.game.npc_dialogue_ui.set_dialogue(npc_name, text, options)
                                self.game.change_state("npc_dialogue")
                                return  # Exit after changing state
                                
                            self.game.conversation_ui.set_dialog(speaker, text, options)
                        else:
                            # Dialogue ended, return to game
                            self.game.change_state("running")

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
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("running")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.merchant_ui.handle_click(event.pos)
            if result == "close":
                self.game.change_state("running")

class JobsBoardState(GameState):
    """Jobs board UI state for displaying available quests."""
    def enter(self):
        # Update quest list when entering
        self.game.jobs_board_ui.update_quests()
    
    def update(self):
        pass
    
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw jobs board UI
        self.game.jobs_board_ui.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("running")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.jobs_board_ui.handle_click(event.pos)
            
            if result == "close":
                # Close button clicked
                self.game.change_state("running")
            elif isinstance(result, dict) and result["action"] == "talk_quest":
                # Talk to specific NPC about quest
                npc_name = result["npc"]
                
                # Start NPC dialogue
                if self.game.quest_manager.start_direct_npc_dialogue(npc_name):
                    # Get dialogue content
                    text = self.game.quest_manager.get_current_text()
                    options = self.game.quest_manager.get_current_options()
                    
                    # Set up NPC dialogue UI
                    self.game.npc_dialogue_ui.set_dialogue(npc_name, text, options)
                    
                    # Change to NPC dialogue state
                    self.game.change_state("npc_dialogue")
                else:
                    print(f"Failed to start dialogue with {npc_name}")

class TextDialogState(GameState):
    """Text dialog UI state for displaying longer text"""
    def enter(self):
        pass
    
    def update(self):
        pass
    
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw text dialog UI
        self.game.text_dialog_ui.draw(screen)
    
    def handle_event(self, event):
        # Handle mouse wheel or other scroll events
        self.game.text_dialog_ui.handle_event(event)
        
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game.change_state("running")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            result = self.game.text_dialog_ui.handle_click(event.pos)
            if result == "close":
                self.game.change_state("running")
            # Handle scrolling
            elif result == "scroll":
                pass  # Already handled in text_dialog_ui

class NPCDialogueState(GameState):
    """NPC dialogue state"""
    def enter(self):
        # Dialogue should already be set up before entering this state
        pass
    
    def update(self):
        pass
    
    def draw(self, screen):
        # Draw game world in background
        screen.fill(BLACK)
        for sprite in self.game.all_sprites:
            screen.blit(sprite.image, self.game.camera.apply(sprite))
        
        # Draw NPC dialogue UI
        self.game.npc_dialogue_ui.draw(screen)
    
    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.game.change_state("running")
            elif event.key >= pygame.K_1 and event.key <= pygame.K_9:
                # Get option index from key (1-9)
                option_index = event.key - pygame.K_1
                
                # Get available options
                options = self.game.quest_manager.get_current_options()
                
                # Select option if valid
                if 0 <= option_index < len(options):
                    self.select_option(option_index)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle UI clicks
            result = self.game.npc_dialogue_ui.handle_click(event.pos)
            
            if result == "close":
                # Close button clicked
                self.game.change_state("running")
            elif isinstance(result, dict) and result["action"] == "select_option":
                # Option button clicked
                self.select_option(result["index"])
    
    def select_option(self, option_index):
        """Select dialogue option and handle result."""
        # Process option selection
        result = self.game.quest_manager.select_option(option_index)
        
        if result:
            # Dialogue continues - update UI
            npc_name = self.game.quest_manager.current_npc.name
            text = self.game.quest_manager.get_current_text()
            options = self.game.quest_manager.get_current_options()
            
            # Update NPC dialogue UI
            self.game.npc_dialogue_ui.set_dialogue(npc_name, text, options)
        else:
            # Dialogue ended
            self.game.change_state("running")