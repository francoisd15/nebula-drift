"""
Configuration file for spaceship game - colors, constants, and settings
"""

# Screen settings
WIDTH = 800
HEIGHT = 600
FPS = 60

# Color palette - unified visual theme
COLORS = {
    # Background
    'bg_space': (5, 5, 15),           # Deep blue-black
    
    # Player
    'player': (240, 240, 255),         # Slightly blue-tinted white
    'player_accent': (100, 200, 255),  # Cyan accent
    'player_cockpit': (80, 220, 255),  # Bright cyan
    'player_engine': (255, 180, 80),   # Orange thrust
    
    # Enemies
    'enemy_basic': (255, 60, 60),      # Bright red
    'enemy_elite': (255, 100, 200),    # Magenta
    'enemy_core': (255, 220, 100),     # Yellow core
    'boss': (200, 40, 40),             # Dark red
    'boss_ring': (255, 120, 60),       # Orange ring
    
    # Debris/Asteroids
    'debris': (140, 140, 150),         # Blue-grey
    'debris_dark': (100, 100, 110),    # Darker grey
    'debris_light': (180, 180, 190),   # Lighter grey
    
    # Projectiles
    'projectile_basic': (100, 220, 255),  # Cyan
    'projectile_power': (255, 220, 100),  # Yellow
    'projectile_heavy': (255, 160, 80),   # Orange
    
    # Explosions
    'explosion_hot': (255, 240, 200),   # White-yellow hot
    'explosion_mid': (255, 160, 60),    # Orange mid
    'explosion_cold': (200, 60, 60),    # Red cool
    
    # Particles
    'particle_thrust': (255, 200, 120), # Orange-white
    'particle_damage': (255, 80, 80),   # Red sparks
    'particle_shield': (100, 220, 255), # Cyan shield
    
    # UI
    'ui_primary': (200, 200, 220),      # Light grey text
    'ui_accent': (100, 200, 255),       # Cyan accent
    'ui_health_high': (80, 255, 80),    # Green
    'ui_health_mid': (255, 255, 80),    # Yellow
    'ui_health_low': (255, 80, 80),     # Red
    'ui_shield': (100, 220, 255),       # Cyan
    'ui_bg': (40, 40, 40),              # Dark UI background
    'ui_border': (80, 80, 80),          # UI borders
    
    # Effects
    'glow_add': (255, 255, 255),        # White for additive blending
    'nebula_purple': (60, 20, 100),     # Purple nebula
    'nebula_blue': (20, 40, 80),        # Blue nebula
    'star_white': (255, 255, 255),      # White stars
    'star_blue': (180, 200, 255),       # Blue stars
    'star_yellow': (255, 240, 200),     # Yellow stars
    'star_red': (255, 180, 180),        # Red stars
}

# Legacy color mappings (for backward compatibility during refactoring)
BLACK = COLORS['bg_space']
WHITE = COLORS['player']
RED = COLORS['enemy_basic']
YELLOW = COLORS['projectile_power']
CYAN = COLORS['projectile_basic']
ORANGE = COLORS['projectile_heavy']
