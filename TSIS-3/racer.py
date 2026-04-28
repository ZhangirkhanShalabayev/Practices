"""
racer.py
========
Contains all game objects and core gameplay logic.

Classes:
  - Player      : the car the user controls
  - EnemyCar    : traffic cars that scroll down
  - Coin        : collectible coins with different values (Practice 11)
  - PowerUp     : Nitro / Shield / Repair pick-ups
  - Obstacle    : road hazards (oil spill, barrier, pothole)
  - NitroStrip  : a road event that gives a speed boost
  - GameState   : owns all objects and runs each frame's game logic
"""

import pygame
import random
import os

# ===========================================================
# SCREEN & ROAD CONSTANTS
# ===========================================================
SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# The road runs from x=60 to x=340 (280 px wide)
ROAD_LEFT   = 60
ROAD_RIGHT  = 340
ROAD_WIDTH  = ROAD_RIGHT - ROAD_LEFT           # 280 px
ROAD_CENTER = (ROAD_LEFT + ROAD_RIGHT) // 2    # 200 px

# The road is divided into 3 equal lanes
LANE_WIDTH = ROAD_WIDTH // 3                   # ~93 px each
LANE_CENTERS = [
    ROAD_LEFT + LANE_WIDTH // 2,               # left lane centre
    ROAD_CENTER,                               # middle lane centre
    ROAD_RIGHT - LANE_WIDTH // 2,              # right lane centre
]

FPS = 60

# ===========================================================
# COLOUR PALETTE
# ===========================================================
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
DARK_BG    = (20,  20,  20)    # outside road (grass / pavement)
ROAD_COLOR = (65,  65,  65)    # road asphalt
YELLOW     = (255, 220, 0)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
BLUE       = (60,  120, 220)
ORANGE     = (255, 140, 0)
DARK_GRAY  = (30,  30,  30)
LIGHT_GRAY = (190, 190, 190)

# ===========================================================
# ASSET HELPER
# ===========================================================
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

def asset(filename: str) -> str:
    """Return the full path to an image in the assets folder."""
    return os.path.join(ASSETS_DIR, filename)


# ===========================================================
# COIN TYPES  (carried over from Practice 11)
# Each coin has a point value and a spawn weight (probability).
# ===========================================================
COIN_TYPES = {
    "coin1.png": {"points": 1, "weight": 50, "name": "Bronze"},
    "coin2.png": {"points": 3, "weight": 30, "name": "Silver"},
    "coin3.png": {"points": 5, "weight": 20, "name": "Gold"},
}

# ===========================================================
# DIFFICULTY SETTINGS
# base_speed  : enemy pixels per frame at game start
# speed_step  : how much to increase speed every SPEED_UP_EVERY coins
# max_enemies : maximum enemy cars allowed on screen at once
# ===========================================================
DIFFICULTY_CONFIG = {
    "easy":   {"base_speed": 4,  "speed_step": 1, "max_enemies": 3},
    "normal": {"base_speed": 6,  "speed_step": 2, "max_enemies": 4},
    "hard":   {"base_speed": 9,  "speed_step": 3, "max_enemies": 5},
}

# Enemy speed increases every N coins collected (from Practice 11)
SPEED_UP_EVERY = 5


# ===========================================================
# ROAD DRAWING
# ===========================================================
def draw_road(surface, scroll_offset):
    """
    Draw the road with:
      - Dark background outside the road
      - Grey asphalt road surface
      - Animated dashed lane dividers (3 lanes)
      - Animated yellow centre-line
      - White solid edge lines
      - Alternating red/white kerb strips on both sides

    scroll_offset increases every frame to make the road look
    like it's moving towards the player.
    """

    # 1. Dark area outside the road (left and right margins)
    surface.fill(DARK_BG)

    # 2. Asphalt rectangle (the actual driving surface)
    pygame.draw.rect(surface, ROAD_COLOR,
                     (ROAD_LEFT, 0, ROAD_WIDTH, SCREEN_HEIGHT))

    # 3. Dashed grey lines separating the 3 lanes
    for lane_x in [ROAD_LEFT + LANE_WIDTH, ROAD_LEFT + LANE_WIDTH * 2]:
        for y in range(-40, SCREEN_HEIGHT, 40):
            pygame.draw.line(
                surface, (95, 95, 95),
                (lane_x, y + scroll_offset),
                (lane_x, y + 20 + scroll_offset),
                2
            )

    # 4. Animated yellow dashed centre line (purely decorative)
    for y in range(-40, SCREEN_HEIGHT, 40):
        pygame.draw.line(
            surface, YELLOW,
            (ROAD_CENTER, y + scroll_offset),
            (ROAD_CENTER, y + 20 + scroll_offset),
            3
        )

    # 5. Solid white lines at the road edges
    pygame.draw.line(surface, WHITE,
                     (ROAD_LEFT,  0), (ROAD_LEFT,  SCREEN_HEIGHT), 4)
    pygame.draw.line(surface, WHITE,
                     (ROAD_RIGHT, 0), (ROAD_RIGHT, SCREEN_HEIGHT), 4)

    # 6. Kerb / rumble strips — alternating red/white blocks
    #    They scroll so they look like real kerb stones
    kerb_h = 30
    for i in range(20):   # draw enough blocks to fill the screen
        ky = (i * kerb_h + scroll_offset * 2) % (SCREEN_HEIGHT + kerb_h * 2) - kerb_h
        color = RED if i % 2 == 0 else WHITE
        pygame.draw.rect(surface, color, (ROAD_LEFT - 10, ky, 10, kerb_h))   # left kerb
        pygame.draw.rect(surface, color, (ROAD_RIGHT,     ky, 10, kerb_h))   # right kerb


# ===========================================================
# BASE CLASS: GameObject
# ===========================================================
class GameObject:
    """
    Base class for every sprite in the game.
    Loads, scales, and draws an image.
    """

    def __init__(self, image_path, size, x, y, speed=0):
        """
        Args:
            image_path : full path to the PNG sprite
            size       : (width, height) to scale the image to
            x, y       : starting centre position
            speed      : pixels per frame to move downward (0 = stationary)
        """
        raw        = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.scale(raw, size)
        self.rect  = self.image.get_rect(center=(x, y))
        self.speed = speed

    def draw(self, surface):
        """Draw this object's sprite onto the surface."""
        surface.blit(self.image, self.rect)


# ===========================================================
# PLAYER CAR
# ===========================================================
class Player(GameObject):
    """
    The car controlled by the player with LEFT / RIGHT arrow keys.
    Can have two power-up states at once:
      - Nitro  : moves sideways faster and the road scrolls faster
      - Shield : the next collision is absorbed instead of killing
    """

    NORMAL_SPEED = 5   # sideways pixels per frame normally
    NITRO_SPEED  = 9   # sideways pixels per frame with Nitro

    def __init__(self, car_color="blue"):
        # Blue car = player.png, Red car = enemy.png (flipped colours)
        img = "player.png" if car_color == "blue" else "enemy.png"
        super().__init__(asset(img), (60, 110), ROAD_CENTER, 500)

        self.shield_active = False   # True → next hit is blocked
        self.nitro_active  = False   # True → move faster
        self.nitro_frames  = 0       # frames of Nitro remaining

    def update(self):
        """Read keyboard and move the player left or right."""
        keys = pygame.key.get_pressed()
        spd  = self.NITRO_SPEED if self.nitro_active else self.NORMAL_SPEED

        if keys[pygame.K_LEFT]  and self.rect.left  > ROAD_LEFT + 2:
            self.rect.x -= spd
        if keys[pygame.K_RIGHT] and self.rect.right < ROAD_RIGHT - 2:
            self.rect.x += spd

        # Count down the Nitro timer each frame
        if self.nitro_active:
            self.nitro_frames -= 1
            if self.nitro_frames <= 0:
                self.nitro_active = False   # Nitro runs out

    def draw(self, surface):
        """Draw the car and a glowing shield ring if Shield is active."""
        super().draw(surface)
        if self.shield_active:
            radius = max(self.rect.width, self.rect.height) // 2 + 10
            pygame.draw.circle(surface, BLUE,          self.rect.center, radius,     3)
            pygame.draw.circle(surface, (140, 200, 255), self.rect.center, radius - 5, 1)

    def activate_nitro(self, seconds=4):
        """Turn on Nitro for the given number of seconds."""
        self.nitro_active = True
        self.nitro_frames = seconds * FPS

    def activate_shield(self):
        """Turn on Shield — it will block the very next collision."""
        self.shield_active = True

    def take_hit(self) -> bool:
        """
        Called when the player crashes into something.
        Returns True  → player is dead (no shield was active).
        Returns False → shield absorbed the hit; player survives.
        """
        if self.shield_active:
            self.shield_active = False   # shield is consumed
            return False                 # survived!
        return True                      # no shield → game over


# ===========================================================
# ENEMY CAR
# ===========================================================
class EnemyCar(GameObject):
    """
    A traffic car that scrolls down the screen.
    Always placed in one of the 3 lanes and respawns at the top
    when it exits at the bottom.
    Uses occupied_lanes to avoid spawning in the same lane as
    another enemy car.
    """

    CAR_W = 56
    CAR_H = 110

    def __init__(self, speed=6, occupied_lanes=None):
        """
        occupied_lanes: set of lane indices (0, 1, 2) already in use,
        so multiple enemies don't overlap in the same lane.
        """
        self.lane_idx = self._pick_lane(occupied_lanes)
        x             = LANE_CENTERS[self.lane_idx]
        super().__init__(asset("enemy.png"),
                         (self.CAR_W, self.CAR_H),
                         x, -120, speed=speed)

    @staticmethod
    def _pick_lane(occupied=None):
        """Return a free lane index, or any lane if all are occupied."""
        all_lanes = [0, 1, 2]
        if occupied:
            free = [l for l in all_lanes if l not in occupied]
            if free:
                return random.choice(free)
        return random.choice(all_lanes)

    def update(self, player_rect):
        """Scroll down and respawn at the top when off-screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn(player_rect)

    def _respawn(self, player_rect):
        """
        Place this car back above the top of the screen.
        Try random positions to avoid overlapping the player.
        """
        for _ in range(15):
            lane = random.choice([0, 1, 2])
            x    = LANE_CENTERS[lane]
            candidate = pygame.Rect(x - self.CAR_W // 2, -160,
                                    self.CAR_W, self.CAR_H)
            if not candidate.colliderect(player_rect):
                self.rect     = candidate
                self.lane_idx = lane
                return
        # Fallback: place in centre lane far above screen
        self.rect.center = (ROAD_CENTER, -250)


# ===========================================================
# COIN  (Practice 11 logic)
# ===========================================================
class Coin(GameObject):
    """
    Collectible coin with three value tiers.
    Bronze (1 pt, 50% chance) → Silver (3 pts, 30%) → Gold (5 pts, 20%).
    Uses weighted random to make higher-value coins rarer.
    """

    def __init__(self, speed=4):
        coin_key = self._pick_type()
        info     = COIN_TYPES[coin_key]
        x        = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
        super().__init__(asset(coin_key), (34, 34), x, -40, speed=speed)
        self.coin_key = coin_key
        self.points   = info["points"]
        self.name     = info["name"]

    @staticmethod
    def _pick_type() -> str:
        """
        Weighted random choice between Bronze / Silver / Gold.
        random.choices uses the 'weights' list so higher-weight
        coins are picked more often.
        """
        keys    = list(COIN_TYPES.keys())
        weights = [COIN_TYPES[k]["weight"] for k in keys]
        return random.choices(keys, weights=weights, k=1)[0]

    def update(self):
        """Scroll down and respawn when off the bottom of the screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self.respawn()

    def respawn(self):
        """Pick a new random type and a new random position."""
        coin_key      = self._pick_type()
        info          = COIN_TYPES[coin_key]
        raw           = pygame.image.load(asset(coin_key)).convert_alpha()
        self.image    = pygame.transform.scale(raw, (34, 34))
        self.coin_key = coin_key
        self.points   = info["points"]
        self.name     = info["name"]
        self.rect.center = (
            random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20), -40
        )


# ===========================================================
# POWER-UPS
# ===========================================================

POWERUP_DATA = {
    "nitro":  {"color": ORANGE, "letter": "N", "label": "Nitro",  "secs": 4},
    "shield": {"color": BLUE,   "letter": "S", "label": "Shield", "secs": 0},
    "repair": {"color": GREEN,  "letter": "R", "label": "Repair", "secs": 0},
}

POWERUP_ON_SCREEN_SECS = 8   # a power-up disappears after this many seconds


class PowerUp:
    """
    A collectible circle on the road showing N / S / R.
    Rules (TSIS 3):
      - Disappears after POWERUP_ON_SCREEN_SECS if not collected
      - Only one power-up active at a time (enforced in GameState)
      - Nitro: speed boost for 4 seconds
      - Shield: absorb next hit
      - Repair: instantly clears all obstacles
    """

    SIZE = 36

    def __init__(self, speed=4):
        self.speed   = speed
        self._font   = None    # font is created lazily (after pygame.init)
        self._spawn_random()

    def _spawn_random(self):
        """Choose a random power-up type and a random screen position."""
        self.kind         = random.choice(list(POWERUP_DATA.keys()))
        data              = POWERUP_DATA[self.kind]
        self.color        = data["color"]
        self.letter       = data["letter"]
        self.life_frames  = POWERUP_ON_SCREEN_SECS * FPS
        self.visible      = True
        x                 = random.randint(ROAD_LEFT + 20, ROAD_RIGHT - 20)
        self.rect         = pygame.Rect(0, 0, self.SIZE, self.SIZE)
        self.rect.center  = (x, -50)

    def update(self):
        """Scroll down; respawn as a new random type when off-screen or timed out."""
        if not self.visible:
            # Wait for the respawn delay to count down
            self.life_frames += 1
            if self.life_frames >= 0:
                self._spawn_random()
            return
        self.rect.y      += self.speed
        self.life_frames -= 1
        if self.rect.top > SCREEN_HEIGHT or self.life_frames <= 0:
            self._spawn_random()

    def collect(self):
        """Called when the player picks up this power-up."""
        self.visible     = False
        self.life_frames = -FPS * 3   # respawn after ~3 seconds

    def draw(self, surface):
        if not self.visible:
            return
        cx, cy = self.rect.center
        r      = self.SIZE // 2
        # Outer glow
        pygame.draw.circle(surface, self.color, (cx, cy), r + 5)
        # White border ring
        pygame.draw.circle(surface, WHITE,      (cx, cy), r + 5, 2)
        # Main filled circle
        pygame.draw.circle(surface, self.color, (cx, cy), r)
        # Lazy-load the font
        if self._font is None:
            self._font = pygame.font.SysFont("Verdana", 16, bold=True)
        txt = self._font.render(self.letter, True, WHITE)
        surface.blit(txt, txt.get_rect(center=(cx, cy)))


# ===========================================================
# OBSTACLE
# ===========================================================

OBSTACLE_KINDS = [
    {"name": "oil",     "color": (15,  15,  60),  "size": (55, 28), "deadly": False},
    {"name": "pothole", "color": (50,  30,  10),  "size": (32, 32), "deadly": True},
    {"name": "barrier", "color": (210, 50,  50),  "size": (70, 18), "deadly": True},
]


class Obstacle:
    """
    A hazard on the road that scrolls downward.
      - Oil spill : non-deadly, just visual (slippery zone)
      - Pothole   : deadly – dodge or use Shield
      - Barrier   : deadly – dodge or use Shield
    After a collision the obstacle is pushed off-screen and
    respawns at the top.
    """

    def __init__(self, speed=5):
        self.speed = speed
        self._pick_kind()
        x         = random.randint(ROAD_LEFT + 35, ROAD_RIGHT - 35)
        self.rect = pygame.Rect(x - self.w // 2, -self.h, self.w, self.h)

    def _pick_kind(self):
        """Randomly choose what type of obstacle this is."""
        kind       = random.choice(OBSTACLE_KINDS)
        self.name  = kind["name"]
        self.color = kind["color"]
        self.w, self.h = kind["size"]
        self.deadly = kind["deadly"]

    def update(self, player_rect):
        """Scroll down; respawn at top when off-screen."""
        self.rect.y += self.speed
        if self.rect.top > SCREEN_HEIGHT:
            self._respawn(player_rect)

    def _respawn(self, player_rect):
        """Place back at the top, safely away from the player."""
        self._pick_kind()
        for _ in range(15):
            x         = random.randint(ROAD_LEFT + 35, ROAD_RIGHT - 35)
            candidate = pygame.Rect(x - self.w // 2, -self.h - 20,
                                    self.w, self.h)
            if not candidate.colliderect(player_rect):
                self.rect = candidate
                return
        self.rect = pygame.Rect(ROAD_CENTER - self.w // 2,
                                -self.h - 20, self.w, self.h)

    def draw(self, surface):
        """Draw the obstacle shaped according to its type."""
        if self.name == "barrier":
            # Striped red/yellow warning barrier
            pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
            stripe_w = 10
            for i in range(self.rect.left, self.rect.right, stripe_w * 2):
                pts = [
                    (i,                              self.rect.top),
                    (min(i + stripe_w, self.rect.right), self.rect.top),
                    (min(i + stripe_w, self.rect.right), self.rect.bottom),
                    (i,                              self.rect.bottom),
                ]
                pygame.draw.polygon(surface, YELLOW, pts)
            pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=3)
        else:
            # Oil / pothole drawn as an ellipse
            pygame.draw.ellipse(surface, self.color, self.rect)
            ring = (70, 70, 120) if self.name == "oil" else (100, 70, 30)
            pygame.draw.ellipse(surface, ring, self.rect, 2)


# ===========================================================
# NITRO STRIP  (road event)
# ===========================================================
class NitroStrip:
    """
    An orange stripe painted across the full road width.
    When the player drives over it they receive a free Nitro boost.
    Spawned at random intervals (managed by GameState).
    """

    HEIGHT   = 22
    LIFETIME = 6 * FPS

    def __init__(self):
        self.rect   = pygame.Rect(ROAD_LEFT, -self.HEIGHT,
                                  ROAD_WIDTH, self.HEIGHT)
        self.speed  = 5
        self.active = False
        self.frames = 0
        self._font  = None

    def spawn(self):
        """Activate the strip at the top of the screen."""
        self.rect.y = -self.HEIGHT
        self.frames = self.LIFETIME
        self.active = True

    def update(self):
        if not self.active:
            return
        self.rect.y -= -self.speed   # scroll down
        self.frames -= 1
        if self.rect.top > SCREEN_HEIGHT or self.frames <= 0:
            self.active = False

    def draw(self, surface):
        if not self.active:
            return
        # Semi-transparent orange band
        band = pygame.Surface((self.rect.width, self.rect.height),
                               pygame.SRCALPHA)
        band.fill((255, 165, 0, 150))
        surface.blit(band, self.rect.topleft)
        pygame.draw.rect(surface, ORANGE, self.rect, 2)
        if self._font is None:
            self._font = pygame.font.SysFont("Verdana", 11, bold=True)
        txt = self._font.render("NITRO ZONE", True, WHITE)
        surface.blit(txt, txt.get_rect(center=self.rect.center))


# ===========================================================
# GAME STATE
# ===========================================================
class GameState:
    """
    Owns every game object and runs all game logic for one run.

    Usage:
        state = GameState("normal", "blue")
        # each frame:
        state.update()
        state.draw(screen)
        if state.game_over: ...
    """

    def __init__(self, difficulty="normal", car_color="blue"):
        cfg                = DIFFICULTY_CONFIG[difficulty]
        self.base_speed    = cfg["base_speed"]
        self.speed_step    = cfg["speed_step"]
        self.max_enemies   = cfg["max_enemies"]
        self.current_speed = self.base_speed
        self.difficulty    = difficulty

        # --- score / progress counters ---
        self.coin_count   = 0      # number of coins collected
        self.total_points = 0      # points from coins (weighted values)
        self.distance_px  = 0      # pixels scrolled = distance travelled
        self.frame        = 0      # frame counter
        self.game_over    = False

        # --- road animation ---
        self.scroll_offset = 0

        # --- active power-up HUD ---
        self.active_powerup_name   = None  # label shown on screen
        self.active_powerup_frames = 0     # how many frames left to show it

        # --- nitro strip spawn timer ---
        self.nitro_timer = random.randint(300, 600)

        # === Create all game objects ===

        self.player = Player(car_color)

        # Start with 2 enemy cars in different lanes, well apart vertically
        self.enemies  = []
        used_lanes    = set()
        for i in range(2):
            e = EnemyCar(speed=self.current_speed, occupied_lanes=used_lanes)
            e.rect.y = -200 - i * 280   # stagger so they aren't bunched
            used_lanes.add(e.lane_idx)
            self.enemies.append(e)

        self.coin      = Coin(speed=max(3, self.current_speed - 2))
        self.powerup   = PowerUp(speed=max(3, self.current_speed - 2))

        # Two obstacles, spaced far apart so they don't appear together
        obs_spd = max(3, self.current_speed - 1)
        self.obstacles = [Obstacle(speed=obs_spd), Obstacle(speed=obs_spd)]
        self.obstacles[1].rect.y = -350

        self.nitro_strip = NitroStrip()

    # ----------------------------------------------------------
    def metres(self) -> int:
        """Distance in metres (pixels ÷ 10)."""
        return self.distance_px // 10

    def score(self) -> int:
        """
        Score = coin points + distance bonus.
        Collecting coins and driving further both increase the score.
        """
        return self.total_points + self.metres() // 5

    # ----------------------------------------------------------
    def update(self):
        """
        Run one frame of game logic.
        Called 60 times per second from main.py.
        """
        if self.game_over:
            return

        self.frame       += 1
        self.distance_px += self.current_speed
        self.scroll_offset = (self.scroll_offset + self.current_speed) % 40

        # --- player input ---
        self.player.update()

        # --- enemy movement ---
        for enemy in self.enemies:
            enemy.update(self.player.rect)

        # --- coin logic ---
        self.coin.update()
        if self.player.rect.colliderect(self.coin.rect):
            self.coin_count   += 1
            self.total_points += self.coin.points
            self.coin.respawn()

            # === Practice 11 difficulty scaling ===
            # Every SPEED_UP_EVERY coins → increase speed
            if self.coin_count % SPEED_UP_EVERY == 0:
                self.current_speed += self.speed_step
                for enemy in self.enemies:
                    enemy.speed = self.current_speed

            # Every 10 coins → add a new enemy (up to max_enemies)
            if self.coin_count % 10 == 0 and len(self.enemies) < self.max_enemies:
                used = {e.lane_idx for e in self.enemies}
                new_e = EnemyCar(speed=self.current_speed, occupied_lanes=used)
                new_e.rect.y = -200
                self.enemies.append(new_e)

        # --- power-up logic ---
        self.powerup.update()
        if self.powerup.visible and self.player.rect.colliderect(self.powerup.rect):
            self._apply_powerup(self.powerup.kind)
            self.powerup.collect()

        # Count down the HUD display timer
        if self.active_powerup_frames > 0:
            self.active_powerup_frames -= 1
        else:
            self.active_powerup_name = None

        # --- obstacle logic ---
        for obs in self.obstacles:
            obs.update(self.player.rect)
            if self.player.rect.colliderect(obs.rect):
                if obs.deadly:
                    if self.player.take_hit():
                        self.game_over = True
                        return
                obs.rect.y = SCREEN_HEIGHT + 100   # push off screen

        # --- enemy collision ---
        for enemy in self.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if self.player.take_hit():
                    self.game_over = True
                    return
                enemy._respawn(self.player.rect)

        # --- nitro strip road event ---
        self.nitro_timer -= 1
        if self.nitro_timer <= 0:
            self.nitro_strip.spawn()
            self.nitro_timer = random.randint(400, 800)
        self.nitro_strip.update()
        if (self.nitro_strip.active
                and self.player.rect.colliderect(self.nitro_strip.rect)):
            self.player.activate_nitro(3)
            self._show_powerup_hud("Nitro", 3)
            self.nitro_strip.active = False

    def _apply_powerup(self, kind: str):
        """Apply the effect of a collected power-up pick-up."""
        if kind == "nitro":
            secs = POWERUP_DATA["nitro"]["secs"]
            self.player.activate_nitro(secs)
            self._show_powerup_hud("Nitro", secs)

        elif kind == "shield":
            self.player.activate_shield()
            self._show_powerup_hud("Shield", 5)

        elif kind == "repair":
            # Instantly remove all obstacles from the screen
            for obs in self.obstacles:
                obs.rect.y = SCREEN_HEIGHT + 100
            self._show_powerup_hud("Repair", 2)

    def _show_powerup_hud(self, name: str, secs: int):
        """Store the power-up name so the HUD can display it."""
        self.active_powerup_name   = name
        self.active_powerup_frames = secs * FPS

    # ----------------------------------------------------------
    def draw(self, surface):
        """Render the complete game scene for this frame."""
        draw_road(surface, self.scroll_offset)
        self.nitro_strip.draw(surface)
        for obs in self.obstacles:
            obs.draw(surface)
        self.coin.draw(surface)
        self.powerup.draw(surface)
        for enemy in self.enemies:
            enemy.draw(surface)
        self.player.draw(surface)
