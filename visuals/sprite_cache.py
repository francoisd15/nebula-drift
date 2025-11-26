"""
Sprite cache system for pre-generated procedural sprites with rotations
"""

import pygame
import math


class SpriteCache:
    """
    Pre-generates and caches rotated sprites for performance.
    """
    
    def __init__(self):
        self.ship_sprites = {}  # {angle: surface}
        self.enemy_sprites = {}  # {enemy_type: surface or {angle: surface}}
        self.asteroid_sprites = []  # List of pre-generated asteroid surfaces
        
        self._generate_ship_sprites()
        self._generate_enemy_sprites()
        self._generate_asteroid_sprites()
    
    def _generate_ship_sprites(self):
        """Generate player ship with detail layers, pre-rotated"""
        # Create base ship on a surface
        base_size = 40
        base = pygame.Surface((base_size, base_size), pygame.SRCALPHA)
        center = base_size // 2
        
        # Ship pointing right (angle 0)
        # Main body (triangle)
        body_points = [
            (center + 15, center),  # Nose
            (center - 10, center - 8),  # Top wing
            (center - 5, center),  # Back center
            (center - 10, center + 8),  # Bottom wing
        ]
        pygame.draw.polygon(base, (240, 240, 255), body_points)
        pygame.draw.polygon(base, (180, 180, 200), body_points, 2)
        
        # Cockpit (glowing cyan circle)
        pygame.draw.circle(base, (80, 220, 255), (center + 3, center), 3)
        
        # Wing details
        pygame.draw.line(base, (180, 180, 200), (center - 8, center - 6), (center + 2, center - 2), 1)
        pygame.draw.line(base, (180, 180, 200), (center - 8, center + 6), (center + 2, center + 2), 1)
        
        # Engine ports (small rectangles at back)
        pygame.draw.circle(base, (100, 100, 120), (center - 10, center - 5), 2)
        pygame.draw.circle(base, (100, 100, 120), (center - 10, center + 5), 2)
        
        # Pre-rotate for all angles (every 1 degree for smooth rotation)
        for angle in range(360):
            rotated = pygame.transform.rotate(base, -angle)
            self.ship_sprites[angle] = rotated
    
    def _generate_enemy_sprites(self):
        """Generate distinct sprites for each enemy type"""
        
        # ScoutDrone: Triangle with core
        scout_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        center = 12
        triangle_points = [
            (center, center - 10),
            (center - 8, center + 8),
            (center + 8, center + 8),
        ]
        pygame.draw.polygon(scout_surf, (255, 60, 60), triangle_points)
        pygame.draw.polygon(scout_surf, (200, 40, 40), triangle_points, 2)
        pygame.draw.circle(scout_surf, (255, 220, 100), (center, center + 2), 4)
        self.enemy_sprites['scout'] = scout_surf
        
        # KamikazeSkiff: Elongated diamond
        kamikaze_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        diamond_points = [
            (center, center - 8),
            (center - 5, center),
            (center, center + 8),
            (center + 5, center),
        ]
        pygame.draw.polygon(kamikaze_surf, (255, 100, 60), diamond_points)
        pygame.draw.polygon(kamikaze_surf, (220, 80, 40), diamond_points, 2)
        self.enemy_sprites['kamikaze'] = kamikaze_surf
        
        # ShieldedFighter: Hexagon
        shielded_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        hex_points = []
        for i in range(6):
            angle = math.radians(i * 60)
            x = center + math.cos(angle) * 8
            y = center + math.sin(angle) * 8
            hex_points.append((x, y))
        pygame.draw.polygon(shielded_surf, (200, 40, 40), hex_points)
        pygame.draw.polygon(shielded_surf, (255, 60, 60), hex_points, 2)
        pygame.draw.circle(shielded_surf, (180, 60, 60), (center, center), 4)
        self.enemy_sprites['shielded'] = shielded_surf
        
        # ZigZagInterceptor: Square with diagonals
        zigzag_surf = pygame.Surface((24, 24), pygame.SRCALPHA)
        square_rect = pygame.Rect(center - 7, center - 7, 14, 14)
        pygame.draw.rect(zigzag_surf, (255, 100, 200), square_rect)
        pygame.draw.rect(zigzag_surf, (220, 80, 180), square_rect, 2)
        pygame.draw.line(zigzag_surf, (220, 80, 180), (center - 7, center - 7), (center + 7, center + 7), 1)
        pygame.draw.line(zigzag_surf, (220, 80, 180), (center + 7, center - 7), (center - 7, center + 7), 1)
        self.enemy_sprites['zigzag'] = zigzag_surf
        
        # Boss: Multi-layer circles (will be animated in game)
        boss_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        boss_center = 30
        # Outer ring
        pygame.draw.circle(boss_surf, (200, 40, 40), (boss_center, boss_center), 24, 3)
        # Middle ring
        pygame.draw.circle(boss_surf, (255, 120, 60), (boss_center, boss_center), 18, 2)
        # Core
        pygame.draw.circle(boss_surf, (255, 220, 100), (boss_center, boss_center), 10)
        pygame.draw.circle(boss_surf, (255, 180, 60), (boss_center, boss_center), 10, 2)
        self.enemy_sprites['boss'] = boss_surf
    
    def _generate_asteroid_sprites(self, count=10):
        """Generate varied asteroid textures"""
        sizes = [12, 16, 20, 24, 28]
        
        for _ in range(count):
            size = sizes[_ % len(sizes)]
            asteroid_surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)
            center = size + 2
            
            # Irregular polygon for asteroid shape
            points = []
            num_points = 7
            for i in range(num_points):
                angle = (360 / num_points) * i
                rad = size + ((-1) ** i) * (size * 0.2)  # Vary radius
                x = center + math.cos(math.radians(angle)) * rad
                y = center + math.sin(math.radians(angle)) * rad
                points.append((x, y))
            
            # Base color variation
            import random
            color_var = random.randint(-20, 20)
            base_color = (140 + color_var, 140 + color_var, 150 + color_var)
            
            pygame.draw.polygon(asteroid_surf, base_color, points)
            pygame.draw.polygon(asteroid_surf, (100, 100, 110), points, 2)
            
            # Add craters (small dark circles)
            for _ in range(random.randint(2, 4)):
                crater_x = center + random.randint(-size//2, size//2)
                crater_y = center + random.randint(-size//2, size//2)
                crater_size = random.randint(2, 4)
                pygame.draw.circle(asteroid_surf, (80, 80, 90), (int(crater_x), int(crater_y)), crater_size)
            
            self.asteroid_sprites.append(asteroid_surf)
    
    def get_ship_sprite(self, angle):
        """Get pre-rotated ship sprite for given angle"""
        # Round to nearest degree
        angle = int(angle) % 360
        return self.ship_sprites.get(angle, self.ship_sprites[0])
    
    def get_enemy_sprite(self, enemy_type):
        """Get enemy sprite by type"""
        return self.enemy_sprites.get(enemy_type, self.enemy_sprites['scout'])
    
    def get_asteroid_sprite(self, index=0):
        """Get asteroid sprite by index"""
        if not self.asteroid_sprites:
            return None
        return self.asteroid_sprites[index % len(self.asteroid_sprites)]
