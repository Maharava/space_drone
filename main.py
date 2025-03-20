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
from ui.inventory_ui import InventoryUI
from ui.jump_ui import JumpUI

# Init pygame
pygame.init()

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Mining Game")

# Game states
GAME_RUNNING = 0
INVENTORY_OPEN = 1
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
jump_ui = JumpUI(map_system)

# Load initial area - Copernicus Belt
print("Attempting to load Copernicus Belt...")
if not map_system.change_area("copernicus-belt"):
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
            elif event.key == pygame.K_ESCAPE and game_state == INVENTORY_OPEN:
                # Close inventory
                game_state = GAME_RUNNING
            elif event.key == pygame.K_SPACE and game_state == GAME_RUNNING:
                # Check if we're triggering a jump
                if jump_ui.visible:
                    if jump_ui.handle_jump():
                        print("Jumped to new area")
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == INVENTORY_OPEN:
            # Handle inventory clicks
            result = inventory_ui.handle_click(event.pos)
            if result == "close":
                game_state = GAME_RUNNING
    
    # Handle space key for continuous firing (only when not jumping)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and game_state == GAME_RUNNING and not jump_ui.visible:
        current_time = pygame.time.get_ticks()
        if current_time - last_shot_time > player.get_weapon_cooldown():
            projectile = player.shoot()
            if projectile:
                all_sprites.add(projectile)
                lasers.add(projectile)
                last_shot_time = current_time
    
    # Update
    all_sprites.update(game_state)
    
    # Update camera to follow player
    camera.update(player)
    
    # Update jump UI
    if game_state == GAME_RUNNING:
        jump_ui.update(player.position)
    
    if game_state == INVENTORY_OPEN:
        inventory_ui.update()
    
    # Check for laser hits on asteroids (only when game running)
    if game_state == GAME_RUNNING:
        hits = pygame.sprite.groupcollide(lasers, asteroids, True, False)
        for projectile, asteroid_list in hits.items():
            for asteroid in asteroid_list:
                # Apply damage based on weapon type
                if asteroid.damage(1):  # TODO: Get actual damage from projectile
                    # Get multiple ores from asteroid
                    ore_drops = asteroid.get_ore_drops()
                    for ore_type in ore_drops:
                        # Create flying ore animation
                        flying_ore = FlyingOre(asteroid.rect.center, ore_type, player)
                        all_sprites.add(flying_ore)
                        flying_ores.add(flying_ore)
                        print(f"Asteroid dropped {ore_type}!")
                    
                    asteroid.kill()
                    # Spawn new asteroid to replace (only if in appropriate area type)
                    if map_system.current_area_id and map_system.areas[map_system.current_area_id]["type"] == "asteroid_field":
                        new_asteroid = Asteroid()
                        all_sprites.add(new_asteroid)
                        asteroids.add(new_asteroid)
    
    # Draw
    screen.fill(BLACK)
    
    # Draw all sprites with camera offset
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))
    
    # Draw jump UI if visible
    if game_state == GAME_RUNNING:
        jump_ui.draw(screen)
    
    # Draw inventory if open
    if game_state == INVENTORY_OPEN:
        inventory_ui.draw(screen)
    else:
        # Draw HUD
        # Get current area name
        area_name = "Unknown Area"
        if map_system.current_area_id and map_system.current_area_id in map_system.areas:
            area_name = map_system.areas[map_system.current_area_id].get("name", map_system.current_area_id)
        
        hud_text = f"Area: {area_name} | Press I for inventory"
        hud_surf = pygame.font.SysFont(None, 24).render(hud_text, True, WHITE)
        screen.blit(hud_surf, (10, 10))
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()