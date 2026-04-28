# game.py — core game logic

import pygame
import random
import time
from config import *


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def rand_cell(exclude=None):
    """Return a random [x, y] aligned to the grid, not in exclude list."""
    exclude = exclude or []
    while True:
        x = random.randrange(0, WIDTH,  CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        if [x, y] not in exclude:
            return [x, y]


def generate_food(snake, obstacles):
    pos = rand_cell(snake + obstacles)
    return {
        "pos":        pos,
        "weight":     random.choice([1, 2, 3]),
        "spawn_time": time.time(),
    }


def generate_poison(snake, obstacles, food_pos):
    pos = rand_cell(snake + obstacles + [food_pos])
    return {"pos": pos, "spawn_time": time.time()}


def generate_powerup(snake, obstacles, food_pos, poison_pos):
    exclude = snake + obstacles + [food_pos]
    if poison_pos:
        exclude.append(poison_pos)
    kind = random.choice(["speed", "slow", "shield"])
    return {
        "pos":       rand_cell(exclude),
        "kind":      kind,
        "spawn_ms":  pygame.time.get_ticks(),
    }


def place_obstacles(snake, level):
    """Place random wall blocks, guaranteed not on snake head."""
    head = snake[0] if snake else [WIDTH//2, HEIGHT//2]
    blocked = list(snake)
    obstacles = []
    count = OBSTACLE_COUNT_PER_LEVEL * (level - OBSTACLES_START_LEVEL + 1)
    attempts = 0
    while len(obstacles) < count and attempts < 2000:
        attempts += 1
        x = random.randrange(0, WIDTH,  CELL_SIZE)
        y = random.randrange(0, HEIGHT, CELL_SIZE)
        cell = [x, y]
        # keep a 3-cell clear zone around head
        if abs(x - head[0]) <= CELL_SIZE*3 and abs(y - head[1]) <= CELL_SIZE*3:
            continue
        if cell not in blocked:
            blocked.append(cell)
            obstacles.append(cell)
    return obstacles


# ──────────────────────────────────────────────
#  Draw helpers
# ──────────────────────────────────────────────

def draw_grid(screen):
    for x in range(0, WIDTH, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


def draw_cell(screen, color, pos):
    pygame.draw.rect(screen, color, [pos[0], pos[1], CELL_SIZE, CELL_SIZE])


FOOD_COLORS = {1: RED, 2: ORANGE, 3: YELLOW}
POWERUP_COLORS = {"speed": BLUE, "slow": CYAN, "shield": PURPLE}
POWERUP_LABELS = {"speed": "SPD", "slow": "SLW", "shield": "SHD"}


# ──────────────────────────────────────────────
#  Main game loop — returns (score, level)
# ──────────────────────────────────────────────

def run_game(screen, clock, settings, username, personal_best):
    font     = pygame.font.SysFont("arial", 22)
    big_font = pygame.font.SysFont("arial", 42)
    sm_font  = pygame.font.SysFont("arial", 17)

    snake_color = tuple(settings["snake_color"])
    show_grid   = settings["grid"]

    # ── state ──
    sx, sy = WIDTH // 2, HEIGHT // 2
    snake  = [[sx, sy]]
    length = 1
    dx, dy = 0, 0
    direction = "STOP"

    score = 0
    level = 1
    speed = 8

    obstacles = []

    food   = generate_food(snake, obstacles)
    poison = generate_poison(snake, obstacles, food["pos"])

    # powerup
    powerup       = generate_powerup(snake, obstacles, food["pos"], poison["pos"])
    active_effect = None   # {"kind": ..., "end_ms": ...}
    shield_active = False
    base_speed    = speed  # speed without effects

    running = True
    result  = None   # will be set to (score, level) on game over

    while running:
        now_ms = pygame.time.get_ticks()

        # ── events ──
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT  and direction != "RIGHT":
                    dx, dy, direction = -CELL_SIZE, 0, "LEFT"
                elif event.key == pygame.K_RIGHT and direction != "LEFT":
                    dx, dy, direction =  CELL_SIZE, 0, "RIGHT"
                elif event.key == pygame.K_UP    and direction != "DOWN":
                    dx, dy, direction = 0, -CELL_SIZE, "UP"
                elif event.key == pygame.K_DOWN  and direction != "UP":
                    dx, dy, direction = 0,  CELL_SIZE, "DOWN"
                elif event.key == pygame.K_ESCAPE:
                    result = (score, level)
                    running = False

        if not running:
            break

        # ── move ──
        hx = snake[-1][0] + dx
        hy = snake[-1][1] + dy
        head = [hx, hy]

        # ── collisions ──
        hit_wall = (hx < 0 or hx >= WIDTH or hy < 0 or hy >= HEIGHT)
        hit_self = head in snake[:-1]
        hit_obs  = head in obstacles

        if hit_wall or hit_self or hit_obs:
            if shield_active:
                shield_active = False
                active_effect = None
                # teleport to center if wall, else just ignore
                if hit_wall:
                    hx = WIDTH  // 2
                    hy = HEIGHT // 2
                    head = [hx, hy]
            else:
                result = (score, level)
                running = False
                break

        snake.append(head)
        if len(snake) > length:
            del snake[0]

        # ── food timer ──
        if time.time() - food["spawn_time"] > FOOD_LIFETIME:
            food = generate_food(snake, obstacles)

        # ── eat food ──
        if head == food["pos"]:
            length += 1
            score  += food["weight"]
            food    = generate_food(snake, obstacles)
            # level up every 3 points
            new_level = score // 3 + 1
            if new_level > level:
                level      = new_level
                base_speed = min(8 + (level - 1) * 2, 25)
                # place obstacles from level 3
                if level >= OBSTACLES_START_LEVEL:
                    obstacles = place_obstacles(snake, level)

        # ── eat poison ──
        if head == poison["pos"]:
            length = max(1, length - POISON_SHORTEN)
            # trim snake list
            while len(snake) > length:
                del snake[0]
            if length <= 1:
                result = (score, level)
                running = False
                break
            poison = generate_poison(snake, obstacles, food["pos"])

        # ── collect powerup ──
        if powerup and head == powerup["pos"]:
            kind = powerup["kind"]
            active_effect = {"kind": kind, "end_ms": now_ms + POWERUP_EFFECT_DURATION}
            if kind == "speed":
                speed = min(base_speed + 6, 30)
            elif kind == "slow":
                speed = max(base_speed - 4, 3)
            elif kind == "shield":
                shield_active = True
            powerup = None  # consumed

        # ── powerup expire on field ──
        if powerup and (now_ms - powerup["spawn_ms"]) > POWERUP_FIELD_DURATION:
            powerup = generate_powerup(snake, obstacles, food["pos"], poison["pos"])

        # ── effect expire ──
        if active_effect and now_ms > active_effect["end_ms"]:
            if active_effect["kind"] in ("speed", "slow"):
                speed = base_speed
            active_effect = None

        # ── spawn new powerup if none ──
        if powerup is None and active_effect is None:
            powerup = generate_powerup(snake, obstacles, food["pos"], poison["pos"])

        # ──────────── DRAW ────────────
        screen.fill(BLACK)
        if show_grid:
            draw_grid(screen)

        # obstacles
        for obs in obstacles:
            draw_cell(screen, BROWN, obs)

        # snake
        for seg in snake:
            draw_cell(screen, snake_color, seg)
        # brighter head
        draw_cell(screen, WHITE, snake[-1])

        # food
        draw_cell(screen, FOOD_COLORS[food["weight"]], food["pos"])

        # poison
        draw_cell(screen, DARK_RED, poison["pos"])

        # powerup
        if powerup:
            draw_cell(screen, POWERUP_COLORS[powerup["kind"]], powerup["pos"])
            lbl = sm_font.render(POWERUP_LABELS[powerup["kind"]], True, WHITE)
            screen.blit(lbl, (powerup["pos"][0], powerup["pos"][1] - 16))

        # HUD
        hud = font.render(
            f"Score: {score}   Level: {level}   Best: {personal_best}",
            True, WHITE
        )
        screen.blit(hud, (10, 10))

        if shield_active:
            sh = font.render("🛡 SHIELD", True, PURPLE)
            screen.blit(sh, (WIDTH - 130, 10))
        elif active_effect:
            lbl = "⚡ SPEED BOOST" if active_effect["kind"] == "speed" else "🐢 SLOW"
            ef  = font.render(lbl, True, BLUE if active_effect["kind"] == "speed" else CYAN)
            screen.blit(ef, (WIDTH - 160, 10))

        pygame.display.update()
        clock.tick(speed)

    return result if result else (score, level)
