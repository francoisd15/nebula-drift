"""
Background rendering: nebula, stars, planets, and screen effects
"""

import pygame
import random
import math


def simple_noise_2d(x, y, seed=0):
    """
    Simple hash-based 2D noise function.
    Returns a value between 0.0 and 1.0
    """
    n = int(x * 374761393 + y * 668265263 + seed * 1664525)
    n = (n ^ (n >> 13)) * 1274126177
    return (n & 0x7fffffff) / 2147483647.0


def generate_nebula(width, height, colors=None):
    """
    Generate a procedural nebula background using noise.
    
    Args:
        width, height: dimensions of the nebula surface
        colors: list of (r, g, b) tuples for nebula colors
    
    Returns:
        pygame Surface with nebula
    """
    if colors is None:
        colors = [(60, 20, 100), (20, 40, 80), (40, 20, 60)]  # Purple/blue hues
    
    nebula = pygame.Surface((width, height), pygame.SRCALPHA)
    
    # Multiple octaves for depth
    for octave in range(3):
        scale = 50 * (2 ** octave)
        color_idx = octave % len(colors)
        base_color = colors[color_idx]
        
        for x in range(0, width, 8):
            for y in range(0, height, 8):
                noise_val = simple_noise_2d(x / scale, y / scale, octave)
                
                if noise_val > 0.4:  # Threshold for visibility
                    alpha = int((noise_val - 0.4) * 100)
                    color = (*base_color, alpha)
                    # Draw slightly larger circles for smooth blending
                    pygame.draw.circle(nebula, color, (x, y), 12)
    
    return nebula


def create_vignette(width, height, max_alpha=100):
    """
    Create a vignette effect (darkening at screen edges).
    
    Args:
        width, height: dimensions
        max_alpha: maximum darkness at edges (0-255)
    
    Returns:
        pygame Surface with vignette
    """
    vignette = pygame.Surface((width, height), pygame.SRCALPHA)
    center_x, center_y = width // 2, height // 2
    max_dist = math.sqrt(center_x ** 2 + center_y ** 2)
    
    # Draw gradient circles from edge to center
    for y in range(0, height, 4):
        for x in range(0, width, 4):
            dist = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            alpha = int((dist / max_dist) * max_alpha)
            pygame.draw.circle(vignette, (0, 0, 0, alpha), (x, y), 4)
    
    return vignette


class ImprovedStarLayer:
    """
    Enhanced star layer with twinkling, colors, and varied brightness.
    """
    
    def __init__(self, count, speed, size_range=(1, 3), brightness=(120, 255), 
                 twinkle=True, colored_star_chance=0.05):
        self.speed = speed
        self.twinkle = twinkle
        self.stars = []
        
        for _ in range(count):
            x = random.randint(0, 800)  # Will be parameterized
            y = random.randint(0, 600)
            size = random.randint(*size_range)
            base_brightness = random.randint(*brightness)
            
            # Some stars are colored
            if random.random() < colored_star_chance:
                # Choose star color: blue, yellow, or red tint
                color_choice = random.choice(['blue', 'yellow', 'red'])
                if color_choice == 'blue':
                    color = (int(base_brightness * 0.7), int(base_brightness * 0.8), base_brightness)
                elif color_choice == 'yellow':
                    color = (base_brightness, int(base_brightness * 0.95), int(base_brightness * 0.8))
                else:  # red
                    color = (base_brightness, int(base_brightness * 0.7), int(base_brightness * 0.7))
            else:
                # White/grey star
                color = (base_brightness, base_brightness, base_brightness)
            
            # Store: [x, y, size, base_color, twinkle_offset, is_bright]
            is_bright = random.random() < 0.05  # 5% bright stars with glow
            self.stars.append([x, y, size, color, random.uniform(0, 360), is_bright])
    
    def update(self, width=800):
        """Update star positions"""
        for s in self.stars:
            s[0] -= self.speed
            if s[0] < 0:
                s[0] = width
                s[1] = random.randint(0, 600)
            
            # Update twinkle offset
            if self.twinkle:
                s[4] = (s[4] + 2) % 360
    
    def draw(self, surf):
        """Draw stars with twinkling effect"""
        for x, y, size, base_color, twinkle_offset, is_bright in self.stars:
            # Calculate twinkling brightness variation
            if self.twinkle:
                twinkle_factor = math.sin(math.radians(twinkle_offset)) * 0.15 + 1.0
                color = tuple(min(255, int(c * twinkle_factor)) for c in base_color)
            else:
                color = base_color
            
            # Draw star
            pygame.draw.circle(surf, color, (int(x), int(y)), size)
            
            # Bright stars get a small glow
            if is_bright:
                glow_alpha = 40
                glow_radius = size + 2
                glow_surf = pygame.Surface((glow_radius * 4, glow_radius * 4), pygame.SRCALPHA)
                glow_color = (*color, glow_alpha)
                pygame.draw.circle(glow_surf, glow_color, (glow_radius * 2, glow_radius * 2), glow_radius)
                surf.blit(glow_surf, 
                         (int(x) - glow_radius * 2, int(y) - glow_radius * 2),
                         special_flags=pygame.BLEND_RGBA_ADD)


class DistantPlanet:
    """
    A distant planet with radial gradient for depth.
    """
    
    def __init__(self, x, y, radius, color1, color2, speed=0.1):
        self.x = x
        self.y = y
        self.radius = radius
        self.color1 = color1  # Center color
        self.color2 = color2  # Edge color
        self.speed = speed
        self.surface = self._generate_planet()
    
    def _generate_planet(self):
        """Pre-generate planet surface with radial gradient"""
        size = self.radius * 2
        planet_surf = pygame.Surface((size, size), pygame.SRCALPHA)
        center = self.radius
        
        # Draw gradient circles from outside to inside
        for r in range(self.radius, 0, -1):
            t = r / self.radius
            # Interpolate colors
            color = tuple(int(self.color1[i] * (1 - t) + self.color2[i] * t) for i in range(3))
            pygame.draw.circle(planet_surf, color, (center, center), r)
        
        return planet_surf
    
    def update(self):
        """Slow drift"""
        self.x -= self.speed
        if self.x < -self.radius:
            self.x = 800 + self.radius
    
    def draw(self, surf):
        """Draw planet"""
        # Low alpha for distant appearance
        surf.blit(self.surface, (int(self.x - self.radius), int(self.y - self.radius)),
                 special_flags=pygame.BLEND_RGBA_MULT)
