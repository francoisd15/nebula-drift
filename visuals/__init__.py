"""
Visual effects and rendering utilities for the spaceship game
"""

from .effects import draw_glow, draw_glow_circle
from .background import generate_nebula, create_vignette, ImprovedStarLayer
from .sprite_cache import SpriteCache

__all__ = [
    'draw_glow',
    'draw_glow_circle',
    'generate_nebula',
    'create_vignette',
    'ImprovedStarLayer',
    'SpriteCache',
]
