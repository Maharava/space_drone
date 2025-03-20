import pygame
from game_config import *

def load_image(name, size=40, prefix="", fallback_color=(100, 100, 100), 
              is_circle=False, first_letter=True):
    """
    Unified image loader that handles both item and module images
    
    Args:
        name (str): Name of the image to load
        size (int): Size of the output image
        prefix (str): Prefix to add before the filename (e.g., "module_")
        fallback_color (tuple): RGB color for fallback image
        is_circle (bool): Whether to draw a circle or rectangle for fallback
        first_letter (bool): Whether to add the first letter to fallback
    
    Returns:
        pygame.Surface: Loaded and scaled image or fallback
    """
    # Format the filename based on the name
    filename = name.lower().replace(" ", "_")
    path = f"assets/{prefix}{filename}.png"
    
    try:
        # Try to load the image
        image = pygame.image.load(path).convert_alpha()
        
        # Scale to requested size (if the original is a different size)
        if image.get_width() != size or image.get_height() != size:
            image = pygame.transform.scale(image, (size, size))
            
        return image
    except:
        # Create fallback image
        surface = pygame.Surface((size, size), pygame.SRCALPHA)
        
        # Draw either circle or rectangle
        if is_circle:
            pygame.draw.circle(surface, fallback_color, (size // 2, size // 2), size // 2)
        else:
            pygame.draw.rect(surface, fallback_color, (0, 0, size, size))
        
        # Add first letter if requested
        if first_letter and name:
            font = pygame.font.SysFont(None, size // 2)
            text = font.render(name[0], True, WHITE)
            surface.blit(text, (size // 2 - text.get_width() // 2, 
                               size // 2 - text.get_height() // 2))
        
        return surface