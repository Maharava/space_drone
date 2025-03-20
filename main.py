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

# Init pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Mining Game")

# Game states
GAME_RUNNING = 0
INVENTORY_OPEN = 1
HANGAR_OPEN = 2
CONVERSATION = 3
MERCHANT_OPEN = 4
game_state = GAME_RUNNING

# Create sprite groups
all_sprites = pygame.sprite.Group()
lasers = pygame.sprite.Group()
asteroids = pygame.sprite.Group()
flying_ores = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Create camera
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

# Create map system
print(f"Working directory: {os.getcwd()}")
print(f"Maps directory exists: {os.path.exists('maps')}")
if os.path.exists('maps'):
    print(f"Files in maps directory: {os.listdir('maps')}")

map_system = MapSystem(all_sprites, asteroids)

# Create UI elements
inventory_ui = InventoryUI(player)
hangar_ui = HangarUI(player)
jump_ui = JumpUI(map_system)
conversation_ui = ConversationUI()
interact_ui = InteractUI()
merchant_ui = MerchantUI(player)

# Load initial area - Copernicus Belt
print("Attempting to load Copernicus Belt...")
if not map_system.change_area("copernicus-belt")[0]:
    print("Failed to load Copernicus Belt! Creating default asteroids...")
    # If we couldn't load the area, create some default asteroids
    for _ in range(40):
        # Mix of asteroid types
        roll = random.random()
        if roll < 0.5:
            asteroid_type = "regular"
        elif roll < 0.8:
            asteroid_type = "dry"
        else:
            asteroid_type = "rich"
            
        asteroid = Asteroid(asteroid_type=asteroid_type)
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

# Game loop
running = True
last_shot_time = 0
shot_cooldown = 300  # milliseconds

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i and game_state == GAME_RUNNING:
                # Open inventory
                game_state = INVENTORY_OPEN
            elif event.key == pygame.K_h and game_state == GAME_RUNNING:
                # Open hangar
                game_state = HANGAR_OPEN
            elif event.key == pygame.K_e and game_state == GAME_RUNNING:
                # Try to interact with nearest station
                station = map_system.get_nearest_station(player.position)
                if station and station.can_interact(player.position):
                    conversation_ui.set_dialog(station.name, station.dialog)
                    game_state = CONVERSATION
            elif event.key == pygame.K_ESCAPE and game_state != GAME_RUNNING:
                # Close UI screens
                game_state = GAME_RUNNING
            elif event.key == pygame.K_SPACE and game_state == GAME_RUNNING:
                # Check if we're triggering a jump
                if jump_ui.visible:
                    success, jump_direction = jump_ui.handle_jump()
                    if success:
                        # Position player at opposite edge based on jump direction
                        if jump_direction == "north":
                            player.position.y = WORLD_HEIGHT - 100
                        elif jump_direction == "south":
                            player.position.y = 100
                        elif jump_direction == "east":
                            player.position.x = 100
                        elif jump_direction == "west":
                            player.position.x = WORLD_WIDTH - 100
                        # Update player rect position
                        player.rect.center = player.position
                        
                        # Set weapon cooldown to max to prevent immediate firing
                        last_shot_time = pygame.time.get_ticks()
                        
                        print(f"Jumped to new area from {jump_direction}")
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == INVENTORY_OPEN:
                # Handle inventory clicks
                result = inventory_ui.handle_click(event.pos)
                if result == "close":
                    game_state = GAME_RUNNING
            elif game_state == HANGAR_OPEN:
                # Handle hangar clicks
                result = hangar_ui.handle_click(event.pos)
                if result == "close":
                    game_state = GAME_RUNNING
            elif game_state == CONVERSATION:
                # Handle conversation clicks
                result = conversation_ui.handle_click(event.pos)
                if result == "close":
                    game_state = GAME_RUNNING
                elif result == "barter":
                    game_state = MERCHANT_OPEN
            elif game_state == MERCHANT_OPEN:
                # Handle merchant clicks
                result = merchant_ui.handle_click(event.pos)
                if result == "close":
                    game_state = GAME_RUNNING
    
    # Handle space key for continuous firing (disable when near jump points)
    keys = pygame.key.get_pressed()
    can_shoot = game_state == GAME_RUNNING and not jump_ui.visible
    if keys[pygame.K_SPACE] and can_shoot:
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time > player.get_weapon_cooldown():
            projectile = player.shoot()
            if projectile:
                all_sprites.add(projectile)
                lasers.add(projectile)
                last_shot_time = current_time
    
    # Update
    if game_state == GAME_RUNNING:
        all_sprites.update(game_state)
    elif game_state == CONVERSATION:
        # Don't update player position during conversation
        for sprite in all_sprites:
            if sprite != player:
                sprite.update(game_state)
    
    # Update camera to follow player
    camera.update(player)
    
    # Update UI elements
    if game_state == GAME_RUNNING:
        jump_ui.update(player.position)
        
        # Check for station interactions
        station = map_system.get_nearest_station(player.position)
        can_interact = station and station.can_interact(player.position)
        interact_ui.update(can_interact, station.name if can_interact else None)
    
    if game_state == INVENTORY_OPEN:
        inventory_ui.update()
    elif game_state == HANGAR_OPEN:
        hangar_ui.update()
    elif game_state == MERCHANT_OPEN:
        merchant_ui.update()
    
    # Handle asteroid respawning
    if game_state == GAME_RUNNING:
        Asteroid.update_respawns(all_sprites, asteroids)
    
    # Check for laser hits on asteroids (only when game running)
    if game_state == GAME_RUNNING:
        hits = pygame.sprite.groupcollide(lasers, asteroids, True, False)
        for projectile, asteroid_list in hits.items():
            for asteroid in asteroid_list:
                # Apply damage based on weapon type
                if asteroid.damage(1):  # TODO: Get actual damage from projectile
                    # Get multiple ores from asteroid
                    ore_drops = asteroid.get_ore_drops()
                    for ore_item in ore_drops:
                        # Create flying ore animation
                        flying_ore = FlyingOre(asteroid.rect.center, ore_item, player)
                        all_sprites.add(flying_ore)
                        flying_ores.add(flying_ore)
                        print(f"Asteroid dropped {ore_item.name}!")
                    
                    # Schedule asteroid respawn at a random edge
                    if map_system.current_area_id and map_system.areas[map_system.current_area_id]["type"] == "asteroid_field":
                        respawn_time = random.randint(30, 90) * FPS  # 30-90 seconds in frames
                        asteroid.schedule_respawn(respawn_time)
                    
                    asteroid.kill()
    
    # Draw
    screen.fill(BLACK)
    
    # Draw all sprites with camera offset
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))
    
    # Draw jump UI if visible
    if game_state == GAME_RUNNING:
        jump_ui.draw(screen)
        interact_ui.draw(screen)
    
    # Draw UI screens if open
    if game_state == INVENTORY_OPEN:
        inventory_ui.draw(screen)
    elif game_state == HANGAR_OPEN:
        hangar_ui.draw(screen)
    elif game_state == CONVERSATION:
        conversation_ui.draw(screen)
    elif game_state == MERCHANT_OPEN:
        merchant_ui.draw(screen)
    else:
        # Draw HUD with background
        hud_bg = pygame.Surface((SCREEN_WIDTH, 30))
        hud_bg.set_alpha(150)
        hud_bg.fill(DARK_GREY)
        screen.blit(hud_bg, (0, 0))
        
        # Get current area name
        area_name = "Unknown Area"
        if map_system.current_area_id and map_system.current_area_id in map_system.areas:
            area_name = map_system.areas[map_system.current_area_id].get("name", map_system.current_area_id)
        
        # Get inventory stats
        used_slots, total_slots = player.get_inventory_capacity()
        
        # Draw area name
        hud_area = pygame.font.SysFont(None, 24).render(f"Area: {area_name}", True, WHITE)
        screen.blit(hud_area, (10, 5))
        
        # Draw silver
        hud_silver = pygame.font.SysFont(None, 24).render(f"Silver: {player.stats.silver}", True, SILVER)
        silver_x = SCREEN_WIDTH // 2 - hud_silver.get_width() // 2
        screen.blit(hud_silver, (silver_x, 5))
        
        # Draw inventory stats
        hud_inv = pygame.font.SysFont(None, 24).render(f"Cargo: {used_slots}/{total_slots}", True, WHITE)
        screen.blit(hud_inv, (SCREEN_WIDTH - hud_inv.get_width() - 10, 5))
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()