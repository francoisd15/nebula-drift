"""
Visual effects: glow, particles, trails, and other rendering effects
"""

import pygame
import math


def draw_glow(surface, color, center, base_radius, glow_layers=3):
    """
    Draw a glowing effect around a point using additive blending.
    
    Args:
        surface: pygame Surface to draw on
        color: RGB tuple (alpha will be calculated)
        center: (x, y) tuple for center position
        base_radius: radius of the core
        glow_layers: number of glow layers (default 3)
    """
    for i in range(glow_layers, 0, -1):
        alpha = int(80 / (i + 1))
        radius = base_radius + i * 4
        glow_color = (*color[:3], alpha)
        
        # Create temporary surface for this glow layer
        glow_surf = pygame.Surface((radius * 4, radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (radius * 2, radius * 2), radius)
        
        # Blit with additive blending for glow effect
        surface.blit(glow_surf, 
                    (center[0] - radius * 2, center[1] - radius * 2),
                    special_flags=pygame.BLEND_RGBA_ADD)


def draw_glow_circle(surface, color, center, radius, glow_layers=3, glow_strength=80):
    """
    Draw a circle with a glow effect.
    
    Args:
        surface: pygame Surface to draw on
        color: RGB tuple for the circle
        center: (x, y) tuple for center position
        radius: radius of the circle
        glow_layers: number of glow layers
        glow_strength: base alpha for glow (0-255)
    """
    # Draw glow layers first
    for i in range(glow_layers, 0, -1):
        alpha = int(glow_strength / (i + 1))
        glow_radius = radius + i * 3
        glow_color = (*color[:3], alpha)
        
        glow_surf = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, glow_color, (glow_radius * 2, glow_radius * 2), glow_radius)
        
        surface.blit(glow_surf,
                    (center[0] - glow_radius * 2, center[1] - glow_radius * 2),
                    special_flags=pygame.BLEND_RGBA_ADD)
    
    # Draw the main circle
    pygame.draw.circle(surface, color, (int(center[0]), int(center[1])), radius)


class ScreenShake:
    """Screen shake effect for impacts and explosions"""
    
    def __init__(self):
        self.offset_x = 0
        self.offset_y = 0
        self.trauma = 0  # 0 to 1
    
    def add_trauma(self, amount):
        """Add trauma (shake intensity). Clamped to 1.0"""
        self.trauma = min(1.0, self.trauma + amount)
    
    def update(self):
        """Update shake offset, decay trauma"""
        import random
        if self.trauma > 0:
            self.trauma -= 0.05
            shake = self.trauma ** 2  # Quadratic falloff for smooth shake
            self.offset_x = random.randint(-int(shake * 10), int(shake * 10))
            self.offset_y = random.randint(-int(shake * 10), int(shake * 10))
        else:
            self.offset_x = 0
            self.offset_y = 0
    
    def apply_offset(self, x, y):
        """Apply shake offset to coordinates"""
        return x + self.offset_x, y + self.offset_y


class HitFlash:
    """White flash effect for damage feedback"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.flash_timer = 0
        self.flash_alpha = 0
    
    def trigger(self, intensity=100):
        """Trigger a flash with given alpha intensity"""
        self.flash_timer = 5  # frames
        self.flash_alpha = intensity
    
    def update(self):
        """Update flash state"""
        if self.flash_timer > 0:
            self.flash_timer -= 1
            self.flash_alpha = int((self.flash_timer / 5) * 100)
    
    def draw(self, surface):
        """Draw flash overlay"""
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash_surf.fill((255, 255, 255, self.flash_alpha))
            surface.blit(flash_surf, (0, 0))
