"""
HUD rendering: health bars, weapon indicators, combo counter, and UI elements
"""

import pygame
import math


def draw_health_bar(surface, x, y, current, maximum, width=150, height=20, 
                   bar_type='health'):
    """
    Draw a graphical health or shield bar.
    
    Args:
        surface: pygame Surface to draw on
        x, y: top-left position
        current: current value
        maximum: maximum value
        width, height: bar dimensions
        bar_type: 'health' or 'shield' for color scheme
    """
    # Background
    bg_rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, (40, 40, 40), bg_rect)
    pygame.draw.rect(surface, (80, 80, 80), bg_rect, 2)
    
    # Fill
    fill_width = int((current / maximum) * width) if current > 0 else 0
    if fill_width > 0:
        fill_rect = pygame.Rect(x, y, fill_width, height)
        
        if bar_type == 'health':
            # Health: green -> yellow -> red based on percentage
            ratio = current / maximum
            if ratio > 0.6:
                color = (80, 255, 80)  # Green
            elif ratio > 0.3:
                color = (255, 255, 80)  # Yellow
            else:
                color = (255, 80, 80)  # Red
        else:  # shield
            # Shield: cyan
            color = (100, 220, 255)
        
        pygame.draw.rect(surface, color, fill_rect)
        
        # Add shine effect (lighter top half)
        shine_rect = pygame.Rect(x, y, fill_width, height // 2)
        shine_surf = pygame.Surface((fill_width, height // 2), pygame.SRCALPHA)
        shine_surf.fill((*color, 60))
        surface.blit(shine_surf, (x, y))
    
    # Value text
    font = pygame.font.SysFont(None, 18)
    text = font.render(f"{int(current)}/{int(maximum)}", True, (200, 200, 220))
    text_rect = text.get_rect(center=(x + width // 2, y + height // 2))
    surface.blit(text, text_rect)


def draw_weapon_indicator(surface, x, y, weapons_dict, active_weapon_id, size=40):
    """
    Draw visual weapon indicator showing all weapons and highlighting active one.
    
    Args:
        surface: pygame Surface
        x, y: starting position
        weapons_dict: dict of {id: weapon_object}
        active_weapon_id: ID of currently active weapon
        size: size of each weapon box
    """
    weapon_colors = {
        1: (100, 220, 255),  # Basic - Cyan
        2: (100, 220, 255),  # Spread - Cyan
        3: (255, 220, 100),  # Piercing - Yellow
        4: (255, 160, 80),   # Torpedo - Orange
    }
    
    offset_x = 0
    for weapon_id in sorted(weapons_dict.keys()):
        weapon = weapons_dict[weapon_id]
        color = weapon_colors.get(weapon_id, (200, 200, 200))
        
        # Box
        box_rect = pygame.Rect(x + offset_x, y, size, size)
        
        # Background
        pygame.draw.rect(surface, (40, 40, 40), box_rect)
        
        # Active weapon gets thick border and glow
        if weapon_id == active_weapon_id:
            # Glow
            glow_surf = pygame.Surface((size + 8, size + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 60), glow_surf.get_rect(), border_radius=4)
            surface.blit(glow_surf, (x + offset_x - 4, y - 4), special_flags=pygame.BLEND_RGBA_ADD)
            
            pygame.draw.rect(surface, color, box_rect, 3, border_radius=4)
        else:
            pygame.draw.rect(surface, (80, 80, 80), box_rect, 2, border_radius=4)
        
        # Weapon icon (simple representation)
        icon_center = (x + offset_x + size // 2, y + size // 2)
        if weapon_id == 1:  # Basic
            pygame.draw.circle(surface, color, icon_center, 6)
        elif weapon_id == 2:  # Spread
            for angle in (-20, 0, 20):
                end_x = icon_center[0] + math.cos(math.radians(angle)) * 10
                end_y = icon_center[1] + math.sin(math.radians(angle)) * 10
                pygame.draw.line(surface, color, icon_center, (end_x, end_y), 2)
        elif weapon_id == 3:  # Piercing
            pygame.draw.line(surface, color, (icon_center[0] - 8, icon_center[1]), 
                           (icon_center[0] + 8, icon_center[1]), 3)
        elif weapon_id == 4:  # Torpedo
            pygame.draw.circle(surface, color, icon_center, 8)
            pygame.draw.circle(surface, color, icon_center, 4)
        
        # Weapon number
        font = pygame.font.SysFont(None, 16)
        num_text = font.render(str(weapon_id), True, (200, 200, 220))
        surface.blit(num_text, (x + offset_x + 2, y + 2))
        
        offset_x += size + 10


def draw_combo_counter(surface, x, y, multiplier, combo_timer, max_combo_time=180):
    """
    Draw stylized combo counter with dynamic sizing and color.
    
    Args:
        surface: pygame Surface
        x, y: center position
        multiplier: combo multiplier value
        combo_timer: frames remaining for combo
        max_combo_time: maximum combo time in frames
    """
    if multiplier <= 1:
        return  # Don't draw if no combo
    
    # Dynamic size based on multiplier
    base_size = 36
    size = base_size + (multiplier - 1) * 4
    
    # Color based on multiplier level
    if multiplier >= 8:
        color = (255, 60, 60)  # Red - high combo
    elif multiplier >= 5:
        color = (255, 160, 60)  # Orange - medium-high
    elif multiplier >= 3:
        color = (255, 220, 100)  # Yellow - medium
    else:
        color = (200, 200, 220)  # White - low
    
    # Pulsation effect
    pulse = math.sin(pygame.time.get_ticks() * 0.01) * 0.1 + 1.0
    draw_size = int(size * pulse)
    
    # Draw combo text
    font = pygame.font.SysFont(None, draw_size)
    text = font.render(f"x{multiplier}", True, color)
    text_rect = text.get_rect(center=(x, y))
    
    # Glow effect
    glow_surf = pygame.Surface((text_rect.width + 20, text_rect.height + 20), pygame.SRCALPHA)
    glow_font = pygame.font.SysFont(None, draw_size + 4)
    glow_text = glow_font.render(f"x{multiplier}", True, (*color, 80))
    glow_rect = glow_text.get_rect(center=(glow_surf.get_width() // 2, glow_surf.get_height() // 2))
    glow_surf.blit(glow_text, glow_rect)
    surface.blit(glow_surf, (text_rect.x - 10, text_rect.y - 10), special_flags=pygame.BLEND_RGBA_ADD)
    
    surface.blit(text, text_rect)
    
    # Combo timer bar below
    if combo_timer > 0:
        bar_width = 100
        bar_height = 4
        bar_x = x - bar_width // 2
        bar_y = y + text_rect.height // 2 + 10
        
        # Background
        pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, bar_width, bar_height))
        
        # Fill
        fill_ratio = combo_timer / max_combo_time
        fill_width = int(bar_width * fill_ratio)
        if fill_width > 0:
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))


def draw_wave_announcement(surface, wave_number, timer, screen_width, screen_height):
    """
    Draw animated wave announcement.
    
    Args:
        surface: pygame Surface
        wave_number: wave number to display
        timer: animation timer (0-120 frames)
        screen_width, screen_height: screen dimensions
    """
    if timer <= 0:
        return
    
    # Slide in from top animation
    progress = min(1.0, timer / 30.0)  # First 30 frames = slide in
    if progress < 1.0:
        y_offset = -100 * (1 - progress)
    else:
        y_offset = 0
    
    # Fade out in last 30 frames
    if timer < 30:
        alpha = int(255 * (timer / 30))
    else:
        alpha = 255
    
    # Main text
    font = pygame.font.SysFont(None, 72)
    text = f"WAVE {wave_number}"
    
    # Text with outline effect
    outline_color = (0, 0, 0, alpha)
    main_color = (255, 255, 255, alpha)
    
    # Create surface for text with alpha
    text_surf = pygame.Surface((screen_width, 100), pygame.SRCALPHA)
    
    # Draw outline (multiple passes for thickness)
    outline_font = pygame.font.SysFont(None, 72)
    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
        outline_text = outline_font.render(text, True, outline_color[:3])
        outline_text.set_alpha(alpha)
        outline_rect = outline_text.get_rect(center=(screen_width // 2 + dx, 50 + dy))
        text_surf.blit(outline_text, outline_rect)
    
    # Draw main text
    main_text = font.render(text, True, main_color[:3])
    main_text.set_alpha(alpha)
    main_rect = main_text.get_rect(center=(screen_width // 2, 50))
    text_surf.blit(main_text, main_rect)
    
    # Blit to screen
    surface.blit(text_surf, (0, int(screen_height // 3 + y_offset)))


def draw_score(surface, x, y, score):
    """
    Draw the player's score.
    
    Args:
        surface: pygame Surface to draw on
        x, y: position for score display
        score: current score value
    """
    # Background box for better visibility
    font = pygame.font.SysFont(None, 32)
    text = font.render(f"Score: {score}", True, (200, 200, 220))
    
    # Background with slight transparency
    bg_padding = 8
    bg_rect = pygame.Rect(x - bg_padding, y - bg_padding, text.get_width() + bg_padding * 2, text.get_height() + bg_padding * 2)
    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
    bg_surf.fill((40, 40, 40, 180))
    surface.blit(bg_surf, (bg_rect.x, bg_rect.y))
    
    # Border
    pygame.draw.rect(surface, (80, 80, 80), bg_rect, 2)
    
    # Score text
    surface.blit(text, (x, y))
