import pygame

def load_image(path, fallback_size=40, fallback_color=(100, 100, 100), fallback_char=None):
    """Load image with fallback if file not found"""
    try:
        image = pygame.image.load(path).convert_alpha()
        return image
    except:
        # Create fallback image
        surface = pygame.Surface((fallback_size, fallback_size), pygame.SRCALPHA)
        pygame.draw.rect(surface, fallback_color, (0, 0, fallback_size, fallback_size))
        
        # Add text if character provided
        if fallback_char:
            font = pygame.font.SysFont(None, fallback_size // 2)
            text = font.render(fallback_char, True, (255, 255, 255))
            surface.blit(text, (
                fallback_size // 2 - text.get_width() // 2,
                fallback_size // 2 - text.get_height() // 2
            ))
        
        return surface
