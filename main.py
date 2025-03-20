import pygame
import sys
from game_config import *
from components.player import Player
from components.asteroid import Asteroid
from components.weapon import Weapon
from components.camera import Camera
from components.engine import Engine
from ui.inventory_ui import InventoryUI

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

# Create player
player = Player()
all_sprites.add(player)

# Create camera
camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)

# Create inventory UI
inventory_ui = InventoryUI(player)

# Create initial asteroids
for _ in range(40):  # More asteroids for larger world
    asteroid = Asteroid()
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
        elif event.type == pygame.MOUSEBUTTONDOWN and game_state == INVENTORY_OPEN:
            # Handle inventory clicks
            result = inventory_ui.handle_click(event.pos)
            if result == "close":
                game_state = GAME_RUNNING
    
    # Handle space key for continuous firing
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and game_state == GAME_RUNNING:
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
                        player.add_ore(ore_type)
                        print(f"Collected {ore_type}!")
                    
                    asteroid.kill()
                    # Spawn new asteroid to replace
                    new_asteroid = Asteroid()
                    all_sprites.add(new_asteroid)
                    asteroids.add(new_asteroid)
    
    # Draw
    screen.fill(BLACK)
    
    # Draw all sprites with camera offset
    for sprite in all_sprites:
        screen.blit(sprite.image, camera.apply(sprite))
    
    # Draw inventory if open
    if game_state == INVENTORY_OPEN:
        inventory_ui.draw(screen)
    else:
        # Draw HUD
        hud_text = f"Ore: {player.total_ore} | Press I for inventory"
        hud_surf = pygame.font.SysFont(None, 24).render(hud_text, True, WHITE)
        screen.blit(hud_surf, (10, 10))
    
    # Update display
    pygame.display.flip()
    clock.tick(FPS)

# Quit
pygame.quit()
sys.exit()