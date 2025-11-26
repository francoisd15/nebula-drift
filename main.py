import pygame
import math
import random
from dataclasses import dataclass

# Import new visual modules
from config import WIDTH, HEIGHT, FPS, COLORS, BLACK, WHITE, RED, YELLOW, CYAN, ORANGE
from visuals import (
    draw_glow, draw_glow_circle, generate_nebula, create_vignette,
    ImprovedStarLayer, SpriteCache
)
from visuals.effects import ScreenShake, HitFlash
from visuals import hud

# Initialize pygame
pygame.init()

# Set up the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Petit Vaisseau Spatial dans l'Espace")

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Initialize visual systems (generated once at startup)
print("Generating procedural visuals...")
sprite_cache = SpriteCache()
nebula_background = generate_nebula(WIDTH, HEIGHT)
vignette_overlay = create_vignette(WIDTH, HEIGHT, max_alpha=80)
screen_shake = ScreenShake()
hit_flash = HitFlash(WIDTH, HEIGHT)
print("Visual systems ready!")

# -----------------------------
# Utility
# -----------------------------

def wrap(x, y):
    return x % WIDTH, y % HEIGHT

# -----------------------------
# Improved parallax star background
# -----------------------------

star_layers = [
    ImprovedStarLayer(60, 0.5, (1, 2), (80, 140), twinkle=True),
    ImprovedStarLayer(80, 1.2, (1, 3), (120, 200), twinkle=True),
    ImprovedStarLayer(100, 2.0, (2, 3), (180, 255), twinkle=True, colored_star_chance=0.08),
]

# -----------------------------
# Player and weapons
# -----------------------------

@dataclass
class Projectile:
    x: float
    y: float
    angle: float
    speed: float
    damage: int
    color: tuple
    radius: int = 3
    life: int = 120
    vx: float = 0.0
    vy: float = 0.0

    def __post_init__(self):
        if self.vx == 0 and self.vy == 0:
            self.vx = math.cos(math.radians(self.angle)) * self.speed
            self.vy = math.sin(math.radians(self.angle)) * self.speed
        self.trail = []  # list of (x, y, alpha)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        self.x, self.y = wrap(self.x, self.y)
        # update trail
        self.trail.append([self.x, self.y, 200])
        if len(self.trail) > 8:
            self.trail.pop(0)
        for t in self.trail:
            t[2] = max(0, t[2] - 30)

    def draw(self, surf):
        # draw trail
        for tx, ty, a in self.trail:
            if a > 0:
                trail_surf = pygame.Surface((self.radius*4, self.radius*4), pygame.SRCALPHA)
                pygame.draw.circle(trail_surf, (*self.color, a), (self.radius*2, self.radius*2), max(1, self.radius-1))
                surf.blit(trail_surf, (int(tx - self.radius*2), int(ty - self.radius*2)), special_flags=pygame.BLEND_RGBA_ADD)
        # glow + core
        draw_glow_circle(surf, self.color, (self.x, self.y), self.radius, glow_layers=2, glow_strength=80)

class Weapon:
    def __init__(self, name):
        self.name = name
        self.cooldown = 8
        self.timer = 0

    def ready(self):
        return self.timer <= 0

    def tick(self):
        if self.timer > 0:
            self.timer -= 1

    def fire(self, px, py, pang):
        self.timer = self.cooldown
        return [Projectile(px, py, pang, 8, 1, CYAN)]

class SpreadShot(Weapon):
    def __init__(self):
        super().__init__("spread")
        self.cooldown = 12

    def fire(self, px, py, pang):
        self.timer = self.cooldown
        shots = []
        for d in (-15, -7, 0, 7, 15):
            shots.append(Projectile(px, py, pang + d, 8, 1, CYAN))
        return shots

class Piercing(Weapon):
    def __init__(self):
        super().__init__("piercing")
        self.cooldown = 10

    def fire(self, px, py, pang):
        self.timer = self.cooldown
        p = Projectile(px, py, pang, 10, 2, YELLOW, radius=3)
        p.life = 240
        return [p]

class Torpedo(Weapon):
    def __init__(self):
        super().__init__("torpedo")
        self.cooldown = 30

    def fire(self, px, py, pang):
        self.timer = self.cooldown
        return [Projectile(px, py, pang, 6, 5, ORANGE, radius=6)]

# Player
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.angle = 0
        self.speed = 5
        self.thrust = False
        self.particles = []
        # Start with a brief spawn invulnerability to avoid instant collisions
        self.invuln = 120  # frames of invulnerability (2 seconds at 60 FPS)
        # survivability
        self.health = 200
        self.shield = 100
        # unlocked weapons: 1-basic, 2-spread, 3-piercing, 4-torpedo (more can be added)
        self.weapons = {
            1: Weapon("basic"),
            2: SpreadShot(),
            3: Piercing(),
            4: Torpedo(),
        }
        self.active_weapon = 1
        # firing feedback
        self.recoil_offset = 0
        self.muzzle_flash_timer = 0

    def switch_weapon(self, idx):
        if idx in self.weapons:
            self.active_weapon = idx

    def fire(self):
        w = self.weapons[self.active_weapon]
        if w.ready():
            # Spawn projectiles a bit further from the ship nose to avoid any overlap
            spawn_offset = 22
            px = self.x + math.cos(math.radians(self.angle)) * spawn_offset
            py = self.y + math.sin(math.radians(self.angle)) * spawn_offset
            
            # Firing feedback effects
            self.recoil_offset = 4  # pixels of recoil
            self.muzzle_flash_timer = 3  # frames
            
            # Muzzle flash particles
            for _ in range(5):
                ang = self.angle + random.uniform(-10, 10)
                ps = random.uniform(4, 7)
                self.particles.append([px, py, ang, ps, random.randint(3, 6), 'muzzle'])
            
            return w.fire(px, py, self.angle)
        return []

    def tick_cooldowns(self):
        for w in self.weapons.values():
            w.tick()
        if self.invuln > 0:
            self.invuln -= 1

    def take_damage(self, dmg):
        if self.invuln > 0:
            return
        # Determine if shield or health was hit for particle color
        shield_hit = self.shield > 0
        if self.shield > 0:
            used = min(self.shield, dmg)
            self.shield -= used
            dmg -= used
        if dmg > 0:
            self.health -= dmg
        self.invuln = 60  # 1 second at 60 FPS
        # hit particles (cyan for shield, red for health)
        particle_color = 'shield' if shield_hit else 'damage'
        for _ in range(15):
            ang = random.uniform(0, 360)
            ps = random.uniform(3, 6)
            self.particles.append([self.x, self.y, ang, ps, random.randint(12, 25), particle_color])

    def update(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.angle -= 5
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.angle += 5
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.thrust = True
            self.x += math.cos(math.radians(self.angle)) * self.speed
            self.y += math.sin(math.radians(self.angle)) * self.speed
            for _ in range(3):
                px = self.x - math.cos(math.radians(self.angle)) * 10
                py = self.y - math.sin(math.radians(self.angle)) * 10
                pang = self.angle + 180 + random.randint(-20, 20)
                ps = random.uniform(2, 5)
                life = random.randint(10, 20)
                self.particles.append([px, py, pang, ps, life, 'thrust'])
        else:
            self.thrust = False

        self.x, self.y = wrap(self.x, self.y)
        
        # Update recoil
        if self.recoil_offset > 0:
            self.recoil_offset -= 1
        if self.muzzle_flash_timer > 0:
            self.muzzle_flash_timer -= 1

        newp = []
        for p in self.particles:
            p[0] += math.cos(math.radians(p[2])) * p[3]
            p[1] += math.sin(math.radians(p[2])) * p[3]
            p[4] -= 1
            if p[4] > 0:
                newp.append(p)
        self.particles = newp

    def draw(self, surf):
        # particles
        for p in self.particles:
            life = p[4]
            max_life = 25 if len(p) > 5 else 20
            alpha = life / max_life
            
            # Determine color based on particle type
            if len(p) > 5:
                ptype = p[5]
                if ptype == 'shield':
                    # Cyan shield sparks
                    color = COLORS['particle_shield']
                elif ptype == 'damage':
                    # Red damage sparks
                    color = COLORS['particle_damage']
                elif ptype == 'muzzle':
                    # White-yellow muzzle flash
                    color = (255, 255, 200)
                else:  # thrust
                    # Orange-white gradient thrust
                    color = COLORS['particle_thrust']
            else:
                # Legacy thrust particles
                color = (255, int(200 * alpha), int(100 * alpha))
            
            # Draw with alpha
            c = (int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha))
            size = 3 if len(p) > 5 and p[5] == 'muzzle' else 2
            pygame.draw.circle(surf, c, (int(p[0]), int(p[1])), size)
        
        # ship (blink when invuln) using sprite cache
        if self.invuln % 10 < 6:
            # Apply recoil offset
            recoil_x = self.x - math.cos(math.radians(self.angle)) * self.recoil_offset
            recoil_y = self.y - math.sin(math.radians(self.angle)) * self.recoil_offset
            
            ship_img = sprite_cache.get_ship_sprite(self.angle)
            rect = ship_img.get_rect(center=(int(recoil_x), int(recoil_y)))
            surf.blit(ship_img, rect)
            
            # Muzzle flash glow
            if self.muzzle_flash_timer > 0:
                flash_x = recoil_x + math.cos(math.radians(self.angle)) * 18
                flash_y = recoil_y + math.sin(math.radians(self.angle)) * 18
                draw_glow(surf, (255, 255, 200), (int(flash_x), int(flash_y)), 4, glow_layers=2)
            
            # Engine glow when thrusting
            if self.thrust:
                draw_glow(surf, (255, 160, 80), (int(recoil_x - math.cos(math.radians(self.angle)) * 12), int(recoil_y - math.sin(math.radians(self.angle)) * 12)), 6, glow_layers=2)

# -----------------------------
# Effects
# -----------------------------

class Explosion:
    def __init__(self, x, y, color=ORANGE, count=12, explosion_type='debris'):
        self.particles = []
        self.explosion_type = explosion_type
        for _ in range(count):
            ang = random.uniform(0, 360)
            spd = random.uniform(2, 5)
            life = random.randint(8, 18)  # Reduced from 15-30 to 8-18
            # Size variety: some larger, some smaller
            size = random.choice([1, 1, 2, 2, 2, 3])  # Reduced max size to 3
            # Fewer long-lived "spark" particles
            if random.random() < 0.08:  # Reduced from 15% to 8% chance
                life = random.randint(20, 30)  # Reduced from 40-60 to 20-30
                spd = random.uniform(3, 5)  # Reduced from 4-7 to 3-5
            self.particles.append([x, y, ang, spd, life, color, size, life])  # added size and max_life

    def update(self):
        alive = []
        for p in self.particles:
            p[0] += math.cos(math.radians(p[2])) * p[3]
            p[1] += math.sin(math.radians(p[2])) * p[3]
            p[3] *= 0.98  # slight velocity decay
            p[4] -= 1
            if p[4] > 0:
                alive.append(p)
        self.particles = alive

    def draw(self, surf):
        for x, y, ang, spd, life, base_color, size, max_life in self.particles:
            # Color gradient: hot (white-yellow) -> mid (orange) -> cold (red)
            life_ratio = life / max_life
            if life_ratio > 0.7:
                # Hot phase: white-yellow
                color = COLORS['explosion_hot']
            elif life_ratio > 0.3:
                # Mid phase: orange
                color = COLORS['explosion_mid']
            else:
                # Cold phase: red (fading out)
                color = COLORS['explosion_cold']
            
            alpha = max(0.2, life / max_life)
            c = (min(255, int(color[0] * alpha)), min(255, int(color[1] * alpha)), min(255, int(color[2] * alpha)))
            pygame.draw.circle(surf, c, (int(x), int(y)), size)

# -----------------------------
# Debris
# -----------------------------

class Debris:
    def __init__(self):
        # spawn at borders heading inward any direction
        edges = [(random.randint(0, WIDTH), -10), (random.randint(0, WIDTH), HEIGHT + 10),
                 (-10, random.randint(0, HEIGHT)), (WIDTH + 10, random.randint(0, HEIGHT))]
        self.x, self.y = random.choice(edges)
        ang = random.uniform(0, 360)
        self.vx = math.cos(math.radians(ang)) * random.uniform(1.5, 3.0)
        self.vy = math.sin(math.radians(ang)) * random.uniform(1.5, 3.0)
        self.size = random.randint(8, 18)
        self.hp = max(1, self.size // 6)
        self.rot = random.uniform(0, 360)
        self.rot_speed = random.uniform(-3, 3)
        self.dead = False
        self.expl_timer = 0
        # choose a sprite index for consistency
        self.sprite_idx = random.randint(0, 9)

    def update(self):
        if self.dead:
            self.expl_timer -= 1
            return
        self.x += self.vx
        self.y += self.vy
        self.rot = (self.rot + self.rot_speed) % 360
        self.x, self.y = wrap(self.x, self.y)

    def hit(self, dmg):
        self.hp -= dmg
        if self.hp <= 0 and not self.dead:
            self.dead = True
            self.expl_timer = 20

    def draw(self, surf):
        if self.dead:
            # Do not draw persistent circle here; Explosion system handles visuals
            return
        # Try sprite-based asteroid, fallback to polygon
        sprite = sprite_cache.get_asteroid_sprite(self.sprite_idx)
        if sprite:
            rotated = pygame.transform.rotate(sprite, -self.rot)
            rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surf.blit(rotated, rect)
        else:
            points = []
            for i in range(6):
                ang = math.radians(self.rot + i * 60)
                rad = self.size + random.randint(-3, 3)
                points.append((self.x + math.cos(ang) * rad, self.y + math.sin(ang) * rad))
            pygame.draw.polygon(surf, (160, 160, 160), points, 2)

# -----------------------------
# Enemies and waves (scaffold)
# -----------------------------

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.hp = 3
        self.dead = False
        self.spawn_alpha = 0  # fade-in effect
        self.spawn_timer = 30  # 0.5 seconds fade in

    def update(self, player):
        # Fade in
        if self.spawn_timer > 0:
            self.spawn_timer -= 1
            self.spawn_alpha = int(255 * (1 - self.spawn_timer / 30))
        else:
            self.spawn_alpha = 255

    def draw(self, surf):
        # Base enemies use simple circle - override in subclasses
        pygame.draw.circle(surf, RED, (int(self.x), int(self.y)), 8, 2)

    def hit(self, dmg):
        self.hp -= dmg
        if self.hp <= 0:
            self.dead = True
    
    def draw_with_alpha(self, surf, sprite):
        """Helper to draw sprite with spawn fade-in alpha"""
        if self.spawn_alpha < 255:
            sprite_copy = sprite.copy()
            sprite_copy.set_alpha(self.spawn_alpha)
            return sprite_copy
        return sprite

class Boss(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.hp = 30
        self.t = 0

    def update(self, player):
        # Ensure spawn fade-in and timers update
        super().update(player)
        self.t += 1
        # slow drift left with sine bobbing (slower so it's hittable)
        self.x -= 0.6
        self.y += math.sin(self.t * 0.04) * 2.0
        self.x, self.y = wrap(self.x, self.y)

    def draw(self, surf):
        img = sprite_cache.get_enemy_sprite('boss')
        img = self.draw_with_alpha(surf, img)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(img, rect)
        # subtle core glow (scaled by spawn alpha)
        if self.spawn_alpha > 50:
            draw_glow(surf, (255, 100, 100), (int(self.x), int(self.y)), 6, glow_layers=2)


class ScoutDrone(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 3.5
        self.hp = 2

    def update(self, player):
        # Ensure spawn fade-in and timers update
        super().update(player)
        # simple chase
        ang = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(ang) * self.speed
        self.y += math.sin(ang) * self.speed
        self.x, self.y = wrap(self.x, self.y)

    def draw(self, surf):
        img = sprite_cache.get_enemy_sprite('scout')
        img = self.draw_with_alpha(surf, img)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(img, rect)

class KamikazeSkiff(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = 5
        self.hp = 1

    def update(self, player):
        # Ensure spawn fade-in and timers update
        super().update(player)
        ang = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(ang) * self.speed
        self.y += math.sin(ang) * self.speed
        self.x, self.y = wrap(self.x, self.y)

    def draw(self, surf):
        img = sprite_cache.get_enemy_sprite('kamikaze')
        img = self.draw_with_alpha(surf, img)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(img, rect)

class ShieldedFighter(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.shield_dir = random.uniform(0, 360)
        self.hp = 5
        self.speed = 2.2

    def update(self, player):
        # Ensure spawn fade-in and timers update
        super().update(player)
        # strafe behavior
        to_player = math.atan2(player.y - self.y, player.x - self.x)
        self.x += math.cos(to_player) * self.speed
        self.y += math.sin(to_player) * self.speed
        self.shield_dir = (self.shield_dir + 2) % 360
        self.x, self.y = wrap(self.x, self.y)

    def draw(self, surf):
        img = sprite_cache.get_enemy_sprite('shielded')
        img = self.draw_with_alpha(surf, img)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(img, rect)
        # draw a small arc to hint at frontal shield (with spawn alpha)
        if self.spawn_alpha > 50:
            ang = math.radians(self.shield_dir)
            sx = self.x + math.cos(ang) * 12
            sy = self.y + math.sin(ang) * 12
            shield_color = (*CYAN[:3], self.spawn_alpha) if self.spawn_alpha < 255 else CYAN
            pygame.draw.circle(surf, shield_color[:3], (int(sx), int(sy)), 6, 1)

class ZigZagInterceptor(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.base_ang = random.uniform(0, 360)
        self.t = 0
        self.hp = 3

    def update(self, player):
        # Ensure spawn fade-in and timers update
        super().update(player)
        self.t += 1
        ang = math.radians(self.base_ang + math.sin(self.t * 0.2) * 60)
        self.x += math.cos(ang) * 3
        self.y += math.sin(ang) * 3
        self.x, self.y = wrap(self.x, self.y)

    def draw(self, surf):
        img = sprite_cache.get_enemy_sprite('zigzag')
        img = self.draw_with_alpha(surf, img)
        rect = img.get_rect(center=(int(self.x), int(self.y)))
        surf.blit(img, rect)

class WaveManager:
    def __init__(self):
        self.wave = 0
        self.spawn_timer = 0
        self.enemies = []
        self.announce_timer = 0

    def update(self, player):
        # spawn next wave when clear
        alive = [e for e in self.enemies if not e.dead]
        self.enemies = alive
        if not self.enemies:
            self.wave += 1
            self.spawn_wave()

        for e in self.enemies:
            e.update(player)

    def draw(self, surf):
        for e in self.enemies:
            e.draw(surf)
        # wave small text
        font = pygame.font.SysFont(None, 24)
        img = font.render(f"Wave {self.wave}", True, WHITE)
        surf.blit(img, (10, 10))
        # announcement overlay (animated)
        if self.announce_timer > 0:
            hud.draw_wave_announcement(surf, self.wave, self.announce_timer, WIDTH, HEIGHT)
            self.announce_timer -= 1

    def spawn_wave(self):
        self.announce_timer = 120
        # boss every 5 waves
        if self.wave % 5 == 0:
            self.enemies.append(Boss(WIDTH + 40, HEIGHT // 2))
            return
        # increase difficulty gradually
        count = min(4 + self.wave, 20)
        for _ in range(count):
            side = random.choice([(random.randint(0, WIDTH), -20), (random.randint(0, WIDTH), HEIGHT + 20),
                                  (-20, random.randint(0, HEIGHT)), (WIDTH + 20, random.randint(0, HEIGHT))])
            x, y = side
            cls = random.choices([
                ScoutDrone, KamikazeSkiff, ShieldedFighter, ZigZagInterceptor
            ], weights=[4, 3, 2, 3], k=1)[0]
            self.enemies.append(cls(x, y))

# -----------------------------
# Power-ups (simple: grant weapon index on pickup)
# -----------------------------

class PowerUp:
    def __init__(self, x, y, weapon_idx):
        self.x = x
        self.y = y
        self.weapon_idx = weapon_idx
        self.t = 0
        self.rotation = 0

    def update(self):
        self.t += 1
        self.rotation = (self.rotation + 3) % 360
        self.y += math.sin(self.t * 0.2) * 0.5
        self.x, self.y = wrap(self.x, self.y)

    def draw(self, surf):
        color = {2: CYAN, 3: YELLOW, 4: ORANGE}.get(self.weapon_idx, WHITE)
        
        # Pulsation
        pulse = math.sin(self.t * 0.1) * 0.2 + 1.0
        radius = int(6 * pulse)
        
        # Glow effect
        draw_glow(surf, color, (int(self.x), int(self.y)), radius, glow_layers=3)
        
        # Core circle
        pygame.draw.circle(surf, color, (int(self.x), int(self.y)), radius, 2)
        
        # Rotating orbit particles
        for i in range(3):
            angle = math.radians(self.rotation + i * 120)
            orbit_x = self.x + math.cos(angle) * 12
            orbit_y = self.y + math.sin(angle) * 12
            pygame.draw.circle(surf, color, (int(orbit_x), int(orbit_y)), 2)

# -----------------------------
# Game state
# -----------------------------

player = Player()
projectiles = []
debris_list = [Debris() for _ in range(6)]
waves = WaveManager()
powerups = []
explosions = []
score = 0
combo_mult = 1
combo_timer = 0  # counts down; resets on player hit; extends on kill
# debris spawning
debris_spawn_timer = random.randint(60, 180)

game_over = False

# spawn initial powerups for testing
for idx in (2, 3, 4):
    powerups.append(PowerUp(random.randint(50, WIDTH-50), random.randint(50, HEIGHT-50), idx))

# Main game loop
running = True
while running:
    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if pygame.K_1 <= event.key <= pygame.K_9:
                player.switch_weapon(event.key - pygame.K_0)
            if event.key == pygame.K_SPACE:
                projectiles.extend(player.fire())

    keys = pygame.key.get_pressed()

    # Update
    for layer in star_layers:
        layer.update()

    if not game_over:
        player.update(keys)
        player.tick_cooldowns()

    for d in debris_list:
        d.update()
    # remove finished debris (after explosion timer)
    debris_list = [d for d in debris_list if not (d.dead and d.expl_timer <= 0)]
    # spawn debris randomly
    debris_spawn_timer -= 1
    if debris_spawn_timer <= 0:
        debris_list.append(Debris())
        debris_spawn_timer = random.randint(45, 150)

    for p in projectiles:
        p.update()
    projectiles = [p for p in projectiles if p.life > 0]

    if not game_over:
        waves.update(player)

    for pu in powerups:
        pu.update()

    # update explosions
    for ex in explosions:
        ex.update()
    explosions = [ex for ex in explosions if ex.particles]

    # decay combo timer
    if combo_timer > 0:
        combo_timer -= 1
    else:
        combo_mult = max(1, combo_mult - 1)

    # Collisions: projectiles with debris and enemies
    def collide(ax, ay, bx, by, r):
        return (ax - bx) ** 2 + (ay - by) ** 2 <= r * r

    # projectile hits
    for p in list(projectiles):
        # debris
        for d in debris_list:
            if not d.dead and collide(p.x, p.y, d.x, d.y, d.size + p.radius):
                d.hit(p.damage)
                p.life = 0
                if d.dead:
                    explosions.append(Explosion(d.x, d.y, ORANGE, 10))
                    screen_shake.add_trauma(0.15)
                    score += 1 * combo_mult
                    combo_mult = min(10, combo_mult + 1)
                    combo_timer = 180  # 3 seconds window to keep combo
        # enemies and boss
        for e in waves.enemies:
            if not e.dead and collide(p.x, p.y, e.x, e.y, 14):
                e.hit(p.damage)
                p.life = 0
                if e.dead:
                    explosions.append(Explosion(e.x, e.y, RED, 15))
                    screen_shake.add_trauma(0.2)
                    score += 5 * combo_mult
                    combo_mult = min(10, combo_mult + 1)
                    combo_timer = 180

    # player collisions with debris and enemies
    if not game_over:
        for d in debris_list:
            if not d.dead and collide(player.x, player.y, d.x, d.y, d.size + 8):
                # Only apply effects if player isn't currently invulnerable
                if player.invuln <= 0:
                    player.take_damage(10)
                    hit_flash.trigger(120)
                    screen_shake.add_trauma(0.25)
                    d.hit(999)
                    explosions.append(Explosion(d.x, d.y, ORANGE, 10))
                    combo_mult = 1
                    combo_timer = 0
        for e in waves.enemies:
            if not e.dead and collide(player.x, player.y, e.x, e.y, 16):
                # Only apply effects if player isn't currently invulnerable
                if player.invuln <= 0:
                    # kamikaze should die on contact
                    player.take_damage(15)
                    hit_flash.trigger(150)
                    screen_shake.add_trauma(0.35)
                    if isinstance(e, KamikazeSkiff):
                        e.dead = True
                    # Only spawn a full explosion if the enemy actually died
                    if e.dead:
                        explosions.append(Explosion(e.x, e.y, RED, 15))
                    combo_mult = 1
                    combo_timer = 0

    # Player pickup powerups
    for pu in list(powerups):
        if collide(player.x, player.y, pu.x, pu.y, 18):
            player.weapons.setdefault(pu.weapon_idx, player.weapons.get(pu.weapon_idx))
            player.switch_weapon(pu.weapon_idx)
            powerups.remove(pu)

    # Prepare render surface and draw
    render_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

    # Background
    render_surf.fill(COLORS['bg_space'])
    render_surf.blit(nebula_background, (0, 0))
    for layer in star_layers:
        layer.draw(render_surf)

    # World elements
    for d in debris_list:
        d.draw(render_surf)

    for p in projectiles:
        p.draw(render_surf)

    for ex in explosions:
        ex.draw(render_surf)

    waves.draw(render_surf)
    player.draw(render_surf)

    # HUD (graphical)
    hud.draw_health_bar(render_surf, 10, HEIGHT - 60, player.health, 100, width=180, height=16, bar_type='health')
    hud.draw_health_bar(render_surf, 10, HEIGHT - 38, player.shield, 50, width=180, height=12, bar_type='shield')
    hud.draw_weapon_indicator(render_surf, WIDTH - 4 * 50 - 20, HEIGHT - 56, player.weapons, player.active_weapon, size=40)
    hud.draw_combo_counter(render_surf, WIDTH // 2, 40, combo_mult, combo_timer, max_combo_time=180)

    # Overlay effects
    render_surf.blit(vignette_overlay, (0, 0))
    hit_flash.update()
    hit_flash.draw(render_surf)

    # Screen shake and final blit
    screen_shake.update()
    screen.fill((0, 0, 0))
    screen.blit(render_surf, (screen_shake.offset_x, screen_shake.offset_y))

    # Game over check and overlay
    if player.health <= 0 and not game_over:
        game_over = True
    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))
        big = pygame.font.SysFont(None, 72)
        txt = big.render("GAME OVER", True, WHITE)
        rect = txt.get_rect(center=(WIDTH//2, HEIGHT//2 - 20))
        screen.blit(txt, rect)
        font = pygame.font.SysFont(None, 24)
        sub = font.render("Press R to restart or ESC to quit", True, WHITE)
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, HEIGHT//2 + 30))

    pygame.display.flip()
    clock.tick(FPS)

    # handle restart/quit in game over state
    if game_over:
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_r:
                    # reset state
                    player.__init__()
                    projectiles.clear()
                    debris_list = [Debris() for _ in range(6)]
                    waves.__init__()
                    powerups.clear()
                    explosions.clear()
                    score = 0
                    combo_mult = 1
                    combo_timer = 0
                    debris_spawn_timer = random.randint(60, 180)
                    game_over = False

pygame.quit()
