import pygame
import sys
import os
import random
from game_config import *
from components.player import Player
from components.asteroid import Asteroid
from components.weapon import Weapon
from components.camera import Camera
from components.engine import Engine
from components.map_system import MapSystem
from components.flying_ore import FlyingOre
from components.space_station import SpaceStation
from ui.inventory_ui import InventoryUI
from ui.hangar_ui import HangarUI
from ui.jump_ui import JumpUI
from ui.conversation_ui import ConversationUI
from ui.interact_ui import InteractUI
from ui.merchant_ui import MerchantUI
from utils import load_image
from quests.quest_manager import QuestManager
from game_state import *
# Use either of these imports:
from quests import QuestManager  # Import from quests package




class Game:
    def __init__(self):
        # Init pygame
        pygame.init()
        
        # Screen setup
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Space Mining Game")
        
        # Game states
        self.states = {
            "running": RunningState(self),
            "inventory": InventoryState(self),
            "hangar": HangarState(self),
            "conversation": ConversationState(self),
            "merchant": MerchantState(self)
        }
        self.current_state = self.states["running"]
        
        # Create sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.lasers = pygame.sprite.Group()
        self.asteroids = pygame.sprite.Group()
        self.flying_ores = pygame.sprite.Group()
        
        # Create player
        self.player = Player()
        self.all_sprites.add(self.player)
        
        # Create camera
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # Create map system
        self.map_system = MapSystem(self.all_sprites, self.asteroids, self)
        
        # Create UI elements
        self.inventory_ui = InventoryUI(self.player)
        self.hangar_ui = HangarUI(self.player)
        self.jump_ui = JumpUI(self.map_system)
        self.conversation_ui = ConversationUI()
        self.interact_ui = InteractUI()
        self.merchant_ui = MerchantUI(self.player)
        
        self.quest_manager = QuestManager(self)
        self.player.game = self
        
        # Load initial area - Copernicus Belt
        if not self.map_system.change_area("copernicus-belt")[0]:
            # Create default asteroids if area load fails
            for _ in range(40):
                roll = random.random()
                if roll < 0.5:
                    asteroid_type = "regular"
                elif roll < 0.8:
                    asteroid_type = "dry"
                else:
                    asteroid_type = "rich"
                    
                asteroid = Asteroid(asteroid_type=asteroid_type)
                self.all_sprites.add(asteroid)
                self.asteroids.add(asteroid)
        
        # Game loop variables
        self.running = True
        self.last_shot_time = 0
    
    def change_state(self, state_name):
        """Change to a different game state"""
        if state_name in self.states:
            self.current_state.exit()
            self.current_state = self.states[state_name]
            self.current_state.enter()
    
    def handle_player_shooting(self):
        """Handle player shooting weapons"""
        keys = pygame.key.get_pressed()
        can_shoot = self.current_state == self.states["running"] and not self.jump_ui.visible
        
        if keys[pygame.K_SPACE] and can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.last_shot_time > self.player.get_weapon_cooldown():
                projectile = self.player.shoot()
                if projectile:
                    self.all_sprites.add(projectile)
                    self.lasers.add(projectile)
                    self.last_shot_time = current_time
    
    def handle_jump(self):
        """Handle player jump to new area"""
        success, jump_direction = self.jump_ui.handle_jump()
        if success:
            # Position player at opposite edge based on jump direction
            if jump_direction == "north":
                self.player.position.y = WORLD_HEIGHT - 100
            elif jump_direction == "south":
                self.player.position.y = 100
            elif jump_direction == "east":
                self.player.position.x = 100
            elif jump_direction == "west":
                self.player.position.x = WORLD_WIDTH - 100
            
            # Update player rect
            self.player.rect.center = self.player.position
            
            # Set weapon cooldown
            self.last_shot_time = pygame.time.get_ticks()
    
    def handle_collision_detection(self):
        """Handle laser hits on asteroids"""
        hits = pygame.sprite.groupcollide(self.lasers, self.asteroids, True, False)
        for projectile, asteroid_list in hits.items():
            for asteroid in asteroid_list:
                if asteroid.damage(1):  # Apply damage
                    # Get ore drops
                    ore_drops = asteroid.get_ore_drops()
                    for ore_item in ore_drops:
                        # Create flying ore animation
                        flying_ore = FlyingOre(asteroid.rect.center, ore_item, self.player)
                        self.all_sprites.add(flying_ore)
                        self.flying_ores.add(flying_ore)
                    
                    # Schedule asteroid respawn
                    if self.map_system.current_area_id and self.map_system.areas[self.map_system.current_area_id]["type"] == "asteroid_field":
                        respawn_time = random.randint(30, 90) * FPS  # 30-90 seconds
                        asteroid.schedule_respawn(respawn_time)
                    
                    asteroid.kill()
    
    def draw_hud(self):
        """Draw heads-up display during gameplay"""
        # HUD background
        hud_bg = pygame.Surface((SCREEN_WIDTH, 30))
        hud_bg.set_alpha(150)
        hud_bg.fill(DARK_GREY)
        self.screen.blit(hud_bg, (0, 0))
        
        # Get area name
        area_name = "Unknown Area"
        if self.map_system.current_area_id and self.map_system.current_area_id in self.map_system.areas:
            area_name = self.map_system.areas[self.map_system.current_area_id].get("name", self.map_system.current_area_id)
        
        # Get inventory stats
        used_slots, total_slots = self.player.get_inventory_capacity()
        
        # Draw area name
        hud_area = pygame.font.SysFont(None, 24).render(f"Area: {area_name}", True, WHITE)
        self.screen.blit(hud_area, (10, 5))
        
        # Draw silver
        hud_silver = pygame.font.SysFont(None, 24).render(f"Silver: {self.player.stats.silver}", True, SILVER)
        silver_x = SCREEN_WIDTH // 2 - hud_silver.get_width() // 2
        self.screen.blit(hud_silver, (silver_x, 5))
        
        # Draw inventory stats
        hud_inv = pygame.font.SysFont(None, 24).render(f"Cargo: {used_slots}/{total_slots}", True, WHITE)
        self.screen.blit(hud_inv, (SCREEN_WIDTH - hud_inv.get_width() - 10, 5))
    
    def draw_fps(self):
        """Draw FPS counter"""
        fps = int(clock.get_fps())
        fps_text = pygame.font.SysFont(None, 20).render(f"FPS: {fps}", True, 
                                                     GREEN if fps >= 55 else 
                                                     YELLOW if fps >= 30 else RED)
        self.screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 5, 35))
    
    def run(self):
        # Game loop
        while self.running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.current_state.handle_event(event)
            
            # Handle shooting (continuous input)
            self.handle_player_shooting()
            
            # Update current state
            self.current_state.update()
            
            # Draw current state
            self.current_state.draw(self.screen)
            
            # Update display
            pygame.display.flip()
            
            # Maintain framerate
            clock.tick(FPS)
        
        # Quit
        pygame.quit()
        sys.exit()

# Main entry point
if __name__ == "__main__":
    game = Game()
    game.run()