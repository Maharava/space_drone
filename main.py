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
map_system = MapSystem(all_sprites, asteroids)

# Create UI elements
inventory_ui = InventoryUI(player)
hangar_ui = HangarUI(player)
jump_ui = JumpUI(map_system)
conversation_ui = ConversationUI()
interact_ui = InteractUI()
merchant_ui = MerchantUI(player)

# Load initial area - Copernicus Belt
if not map_system.change_area("copernicus-belt")[0]:
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
        all_sprites.add(asteroid)
        asteroids.add(asteroid)

# Game loop variables
running = True
last_shot_time = 0


def change_game_state(new_state):
    """Safely change game state with proper transitions"""
    global game_state
    
    # Handle exit from current state
    if game_state == CONVERSATION and new_state != MERCHANT_OPEN:
        # Clean up conversation state if needed
        pass
        
    # Set new state
    game_state = new_state
    
    # Handle entry to new state
    if new_state == INVENTORY_OPEN:
        inventory_ui.update()
    elif new_state == HANGAR_OPEN:
        hangar_ui.update()
    elif new_state == MERCHANT_OPEN:
        merchant_ui.update()


def handle_player_shooting():
    """Handle player shooting weapons"""
    global last_shot_time
    
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


def handle_jump():
    """Handle player jump to new area"""
    global last_shot_time
    
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
        
        # Update player rect
        player.rect.center = player.position
        
        # Set weapon cooldown
        last_shot_time = pygame.time.get_ticks()


def handle_gameplay_events(event):
    """Handle events during gameplay"""
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_i:
            change_game_state(INVENTORY_OPEN)
        elif event.key == pygame.K_h:
            change_game_state(HANGAR_OPEN)
        elif event.key == pygame.K_e:
            # Try to interact with nearest station
            station = map_system.get_nearest_station(player.position)
            if station and station.can_interact(player.position):
                conversation_ui.set_dialog(station.name, station.dialog)
                change_game_state(CONVERSATION)
        elif event.key == pygame.K_SPACE:
            # Check for jump
            if jump_ui.visible:
                handle_jump()


def handle_ui_events(event):
    """Handle UI screen events"""
    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
        change_game_state(GAME_RUNNING)
    elif event.type == pygame.MOUSEBUTTONDOWN:
        if game_state == INVENTORY_OPEN:
            result = inventory_ui.handle_click(event.pos)
            if result == "close":
                change_game_state(GAME_RUNNING)
        elif game_state == HANGAR_OPEN:
            result = hangar_ui.handle_click(event.pos)
            if result == "close":
                change_game_state(GAME_RUNNING)
        elif game_state == CONVERSATION:
            result = conversation_ui.handle_click(event.pos)
            if result == "close":
                change_game_state(GAME_RUNNING)
            elif result == "barter":
                change_game_state(MERCHANT_OPEN)
        elif game_state == MERCHANT_OPEN:
            result = merchant_ui.handle_click(event.pos)
            if result == "close":
                change_game_state(GAME_RUNNING)


def handle_collision_detection():
    """Handle laser hits on asteroids"""
    if game_state != GAME_RUNNING:
        return
        
    hits = pygame.sprite.groupcollide(lasers, asteroids, True, False)
    for projectile, asteroid_list in hits.items():
        for asteroid in asteroid_list:
            if asteroid.damage(1):  # Apply damage
                # Get ore drops
                ore_drops = asteroid.get_ore_drops()
                for ore_item in ore_drops:
                    # Create flying ore animation
                    flying_ore = FlyingOre(asteroid.rect.center, ore_item, player)
                    all_sprites.add(flying_ore)
                    flying_ores.add(flying_ore)
                
                # Schedule asteroid respawn
                if map_system.current_area_id and map_system.areas[map_system.current_area_id]["type"] == "asteroid_field":
                    respawn_time = random.randint(30, 90) * FPS  # 30-90 seconds
                    asteroid.schedule_respawn(respawn_time)
                
                asteroid.kill()


def update_game():
    """Update game state"""
    # Update sprites
    if game_state == GAME_RUNNING:
        all_sprites.update(game_state)
    elif game_state == CONVERSATION:
        # Don't update player during conversation
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
    
    # Update appropriate UI
    if game_state == INVENTORY_OPEN:
        inventory_ui.update()
    elif game_state == HANGAR_OPEN:
        hangar_ui.update()
    elif game_state == MERCHANT_OPEN:
        merchant_ui.update()
    
    # Handle asteroid respawning
    if game_state == GAME_RUNNING:
        Asteroid.update_respawns(all_sprites, asteroids)
    
    # Handle collisions
    handle_collision_detection()


def draw_hud():
    """Draw heads-up display during gameplay"""
    # HUD background
    hud_bg = pygame.Surface((SCREEN_WIDTH, 30))
    hud_bg.set_alpha(150)
    hud_bg.fill(DARK_GREY)
    screen.blit(hud_bg, (0, 0))
    
    # Get area name
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


def draw_fps():
    """Draw FPS counter"""
    fps = int(clock.get_fps())
    fps_text = pygame.font.SysFont(None, 20).render(f"FPS: {fps}", True, 
                                                 GREEN if fps >= 55 else 
                                                 YELLOW if fps >= 30 else RED)
    screen.blit(fps_text, (SCREEN_WIDTH - fps_text.get_width() - 5, 35))


def draw_game():
    """Draw game elements"""
    # Clear screen
    screen.fill(BLACK)
    
    # Draw sprites with camera offset
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))
    
    # Draw appropriate UI
    if game_state == GAME_RUNNING:
        jump_ui.draw(screen)
        interact_ui.draw(screen)
        draw_hud()
        draw_fps()
    elif game_state == INVENTORY_OPEN:
        inventory_ui.draw(screen)
    elif game_state == HANGAR_OPEN:
        hangar_ui.draw(screen)
    elif game_state == CONVERSATION:
        conversation_ui.draw(screen)
    elif game_state == MERCHANT_OPEN:
        merchant_ui.draw(screen)
    
    # Update display
    pygame.display.flip()


# Game loop
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == GAME_RUNNING:
            handle_gameplay_events(event)
        else:
            handle_ui_events(event)
    
    # Handle shooting (continuous input)
    handle_player_shooting()
    
    # Update game state
    update_game()
    
    # Draw everything
    draw_game()
    
    # Maintain framerate
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()