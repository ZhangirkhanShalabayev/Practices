"""
ui.py
=====
All Pygame screens and the in-game HUD.
No external UI libraries — only built-in Pygame drawing.

Screens:
  main_menu()         → "play" | "leaderboard" | "settings" | "quit"
  username_screen()   → player name string
  settings_screen()   → updated settings dict
  leaderboard_screen()→ (no return, just display)
  game_over_screen()  → "retry" | "menu"
  draw_hud()          → drawn on top of the game every frame
"""

import pygame
from racer import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    WHITE, BLACK, DARK_BG, ROAD_COLOR,
    YELLOW, RED, GREEN, BLUE, ORANGE, DARK_GRAY, LIGHT_GRAY,
    POWERUP_DATA
)

# ===========================================================
# SHARED COLOURS (extra UI colours)
# ===========================================================
UI_BG        = (18, 18, 28)    # deep dark background for menus
PANEL_BG     = (30, 30, 45)    # card / panel background
BORDER_COLOR = (70, 70, 100)   # subtle border
ACCENT       = (255, 200, 0)   # bright yellow accent


# ===========================================================
# HELPER: draw a rounded button and return its Rect
# ===========================================================
def draw_button(surface, text, x, y, w=200, h=46,
                bg=PANEL_BG, fg=WHITE, border=BORDER_COLOR,
                font_size=20):
    """
    Draw a rounded rectangle button with centred text.
    Returns the pygame.Rect so the caller can check mouse clicks.
    """
    rect = pygame.Rect(x, y, w, h)
    pygame.draw.rect(surface, bg,     rect, border_radius=10)
    pygame.draw.rect(surface, border, rect, 2, border_radius=10)
    font = pygame.font.SysFont("Verdana", font_size, bold=True)
    lbl  = font.render(text, True, fg)
    surface.blit(lbl, lbl.get_rect(center=rect.center))
    return rect


def draw_title(surface, text, y, color=ACCENT, size=34):
    """Draw bold centred title text."""
    font = pygame.font.SysFont("Verdana", size, bold=True)
    lbl  = font.render(text, True, color)
    surface.blit(lbl, lbl.get_rect(centerx=SCREEN_WIDTH // 2, y=y))


def fill_bg(surface):
    """Fill the screen with the standard menu background."""
    surface.fill(UI_BG)
    # Subtle decorative lines on the sides (like a road)
    for x in [30, SCREEN_WIDTH - 30]:
        pygame.draw.line(surface, PANEL_BG, (x, 0), (x, SCREEN_HEIGHT), 2)


# ===========================================================
# MAIN MENU
# ===========================================================
def main_menu(surface, clock):
    """
    Show the main menu with four buttons.
    Returns the player's choice as a string.
    """
    while True:
        fill_bg(surface)

        # Title
        draw_title(surface, "RACER", 55, color=ACCENT, size=52)

        # Decorative horizontal line under the title
        pygame.draw.line(surface, BORDER_COLOR,
                         (40, 148), (SCREEN_WIDTH - 40, 148), 1)

        # Buttons — each returns a Rect for collision detection
        cx        = SCREEN_WIDTH // 2
        play_btn  = draw_button(surface, "PLAY",        cx - 90, 170, w=180, bg=(40, 160, 70),  h=50)
        lb_btn    = draw_button(surface, "LEADERBOARD", cx - 90, 235, w=180, bg=(180, 100, 20), h=50)
        set_btn   = draw_button(surface, "SETTINGS",    cx - 90, 300, w=180, bg=(30, 90, 180),  h=50)
        quit_btn  = draw_button(surface, "QUIT",        cx - 90, 365, w=180, bg=(160, 30, 30),  h=50)

        # Footer
        footer = pygame.font.SysFont("Verdana", 13)
        f_lbl  = footer.render("Arrow Keys to move  |  ESC to pause", True, (80, 80, 100))
        surface.blit(f_lbl, f_lbl.get_rect(centerx=cx, y=SCREEN_HEIGHT - 30))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if play_btn.collidepoint(pos):  return "play"
                if lb_btn.collidepoint(pos):    return "leaderboard"
                if set_btn.collidepoint(pos):   return "settings"
                if quit_btn.collidepoint(pos):  return "quit"


# ===========================================================
# USERNAME ENTRY
# ===========================================================
def username_screen(surface, clock, default="Player"):
    """
    Let the player type their name before the game starts.
    Returns the entered name as a string.
    """
    name           = list(default)
    cursor_visible = True
    tick           = 0

    while True:
        fill_bg(surface)
        draw_title(surface, "ENTER YOUR NAME", 100)

        # Input box
        box = pygame.Rect(SCREEN_WIDTH // 2 - 140, 165, 280, 54)
        pygame.draw.rect(surface, PANEL_BG,     box, border_radius=8)
        pygame.draw.rect(surface, ACCENT,       box, 2, border_radius=8)

        # Blinking cursor
        tick += 1
        if tick % 30 == 0:
            cursor_visible = not cursor_visible
        display = "".join(name) + ("|" if cursor_visible else " ")

        name_font = pygame.font.SysFont("Verdana", 24, bold=True)
        lbl       = name_font.render(display, True, WHITE)
        surface.blit(lbl, lbl.get_rect(center=box.center))

        # Hint text
        hint_font = pygame.font.SysFont("Verdana", 15)
        hint      = hint_font.render("Type your name, then press ENTER", True, LIGHT_GRAY)
        surface.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=232))

        start_btn = draw_button(surface, "START RACING",
                                SCREEN_WIDTH // 2 - 100, 275,
                                w=200, bg=(40, 160, 70), h=48, font_size=19)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "Player"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "".join(name).strip() or "Player"
                elif event.key == pygame.K_BACKSPACE:
                    if name:
                        name.pop()
                elif event.unicode and len(name) < 16:
                    name.append(event.unicode)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if start_btn.collidepoint(event.pos):
                    return "".join(name).strip() or "Player"


# ===========================================================
# SETTINGS SCREEN
# ===========================================================
def settings_screen(surface, clock, settings: dict) -> dict:
    """
    Let the player toggle sound, pick a car colour, and choose difficulty.
    Returns the (possibly modified) settings dict.
    All changes take effect immediately when Save is clicked.
    """
    s = settings.copy()   # work on a copy so ESC can cancel

    while True:
        fill_bg(surface)
        draw_title(surface, "SETTINGS", 35)
        pygame.draw.line(surface, BORDER_COLOR,
                         (40, 80), (SCREEN_WIDTH - 40, 80), 1)

        label_font = pygame.font.SysFont("Verdana", 18, bold=True)
        val_font   = pygame.font.SysFont("Verdana", 16)

        # --- Sound ---
        surface.blit(label_font.render("Sound", True, LIGHT_GRAY), (50, 105))
        sound_btn = draw_button(surface,
                                "ON" if s["sound"] else "OFF",
                                230, 98, w=110, h=36,
                                bg=(40, 160, 70) if s["sound"] else (160, 40, 40))

        # --- Car colour ---
        surface.blit(label_font.render("Car Colour", True, LIGHT_GRAY), (50, 165))
        blue_btn = draw_button(surface, "Blue", 200, 158, w=65, h=36,
                               bg=(30, 90, 180) if s["car_color"] == "blue" else PANEL_BG,
                               border=BLUE)
        red_btn  = draw_button(surface, "Red",  278, 158, w=65, h=36,
                               bg=(160, 40, 40) if s["car_color"] == "red" else PANEL_BG,
                               border=RED)

        # --- Difficulty ---
        surface.blit(label_font.render("Difficulty", True, LIGHT_GRAY), (50, 225))
        def diff_bg(d):
            return {"easy": (30, 130, 50), "normal": (180, 100, 20), "hard": (160, 30, 30)}[d]
        easy_btn = draw_button(surface, "Easy",   80,  218, w=75, h=36,
                               bg=diff_bg("easy")   if s["difficulty"] == "easy"   else PANEL_BG)
        norm_btn = draw_button(surface, "Normal", 165, 218, w=85, h=36,
                               bg=diff_bg("normal") if s["difficulty"] == "normal" else PANEL_BG)
        hard_btn = draw_button(surface, "Hard",   260, 218, w=75, h=36,
                               bg=diff_bg("hard")   if s["difficulty"] == "hard"   else PANEL_BG)

        # --- Save / Back ---
        pygame.draw.line(surface, BORDER_COLOR,
                         (40, 275), (SCREEN_WIDTH - 40, 275), 1)
        save_btn = draw_button(surface, "Save & Back",
                               SCREEN_WIDTH // 2 - 95, 295,
                               w=190, h=46, bg=(40, 160, 70), font_size=19)

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return s
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return settings   # cancel — return original unchanged
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if sound_btn.collidepoint(pos):  s["sound"]      = not s["sound"]
                if blue_btn.collidepoint(pos):   s["car_color"]  = "blue"
                if red_btn.collidepoint(pos):    s["car_color"]  = "red"
                if easy_btn.collidepoint(pos):   s["difficulty"] = "easy"
                if norm_btn.collidepoint(pos):   s["difficulty"] = "normal"
                if hard_btn.collidepoint(pos):   s["difficulty"] = "hard"
                if save_btn.collidepoint(pos):   return s


# ===========================================================
# LEADERBOARD SCREEN
# ===========================================================
def leaderboard_screen(surface, clock, entries: list):
    """
    Show the top-10 saved scores in a table.
    entries is a list of dicts: {name, score, distance, coins}
    """
    row_font  = pygame.font.SysFont("Verdana", 16)
    head_font = pygame.font.SysFont("Verdana", 14, bold=True)

    while True:
        fill_bg(surface)
        draw_title(surface, "LEADERBOARD", 25, size=28)
        pygame.draw.line(surface, BORDER_COLOR,
                         (30, 65), (SCREEN_WIDTH - 30, 65), 1)

        # Column headers
        cols    = ["#",  "Name",  "Score", "Dist", "Coins"]
        col_xs  = [18,   48,      175,     255,    320]
        for header, x in zip(cols, col_xs):
            lbl = head_font.render(header, True, ACCENT)
            surface.blit(lbl, (x, 72))
        pygame.draw.line(surface, BORDER_COLOR,
                         (30, 92), (SCREEN_WIDTH - 30, 92), 1)

        if not entries:
            empty = row_font.render("No scores yet — play a game first!", True, LIGHT_GRAY)
            surface.blit(empty, empty.get_rect(centerx=SCREEN_WIDTH // 2, y=200))
        else:
            for rank, entry in enumerate(entries[:10], start=1):
                y = 97 + (rank - 1) * 36

                # Alternating row background
                row_bg = (35, 35, 55) if rank % 2 == 0 else (28, 28, 46)
                pygame.draw.rect(surface, row_bg,
                                 pygame.Rect(15, y, SCREEN_WIDTH - 30, 33),
                                 border_radius=5)

                # Gold / silver / bronze colour for top 3
                if rank == 1:
                    row_color = (255, 215, 0)
                elif rank == 2:
                    row_color = (200, 200, 200)
                elif rank == 3:
                    row_color = (205, 127, 50)
                else:
                    row_color = LIGHT_GRAY

                values = [
                    str(rank),
                    entry.get("name", "?")[:10],
                    str(entry.get("score", 0)),
                    f'{entry.get("distance", 0)}m',
                    str(entry.get("coins", 0)),
                ]
                for val, x in zip(values, col_xs):
                    lbl = row_font.render(val, True, row_color)
                    surface.blit(lbl, (x, y + 8))

        back_btn = draw_button(surface, "Back to Menu",
                               SCREEN_WIDTH // 2 - 90, 530,
                               w=180, h=44, bg=(30, 90, 180))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_btn.collidepoint(event.pos):
                    return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return


# ===========================================================
# GAME OVER SCREEN
# ===========================================================
def game_over_screen(surface, clock, score, distance, coins, username):
    """
    Show final stats and let the player retry or return to menu.
    Returns "retry" or "menu".
    """
    big_font  = pygame.font.SysFont("Verdana", 38, bold=True)
    med_font  = pygame.font.SysFont("Verdana", 20)
    stat_font = pygame.font.SysFont("Verdana", 17)

    while True:
        fill_bg(surface)

        # --- GAME OVER title ---
        lbl = big_font.render("GAME OVER", True, RED)
        surface.blit(lbl, lbl.get_rect(centerx=SCREEN_WIDTH // 2, y=55))

        pygame.draw.line(surface, BORDER_COLOR,
                         (40, 110), (SCREEN_WIDTH - 40, 110), 1)

        # --- Player name ---
        name_lbl = med_font.render(f"Driver:  {username}", True, ACCENT)
        surface.blit(name_lbl, name_lbl.get_rect(centerx=SCREEN_WIDTH // 2, y=125))

        # --- Stats panel ---
        panel = pygame.Rect(60, 160, SCREEN_WIDTH - 120, 140)
        pygame.draw.rect(surface, PANEL_BG, panel, border_radius=10)
        pygame.draw.rect(surface, BORDER_COLOR, panel, 1, border_radius=10)

        stats = [
            ("Score",    str(score)),
            ("Distance", f"{distance} m"),
            ("Coins",    str(coins)),
        ]
        for i, (label, value) in enumerate(stats):
            y = 175 + i * 38
            # Label on the left
            lbl = stat_font.render(label, True, LIGHT_GRAY)
            surface.blit(lbl, (80, y))
            # Value on the right (right-aligned)
            val_lbl = stat_font.render(value, True, WHITE)
            surface.blit(val_lbl, val_lbl.get_rect(right=panel.right - 15, y=y))

        pygame.draw.line(surface, BORDER_COLOR,
                         (40, 315), (SCREEN_WIDTH - 40, 315), 1)

        # --- Buttons ---
        retry_btn = draw_button(surface, "Retry",
                                SCREEN_WIDTH // 2 - 165, 335,
                                w=150, h=48, bg=(40, 160, 70), font_size=20)
        menu_btn  = draw_button(surface, "Main Menu",
                                SCREEN_WIDTH // 2 + 15,  335,
                                w=150, h=48, bg=(30, 90, 180), font_size=20)

        hint = pygame.font.SysFont("Verdana", 13).render(
            "R = Retry   |   M = Menu", True, (70, 70, 90))
        surface.blit(hint, hint.get_rect(centerx=SCREEN_WIDTH // 2, y=398))

        pygame.display.flip()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                pos = event.pos
                if retry_btn.collidepoint(pos): return "retry"
                if menu_btn.collidepoint(pos):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_m: return "menu"


# ===========================================================
# HUD — drawn every frame during gameplay
# ===========================================================
def draw_hud(surface, state, username):
    """
    Draw the heads-up display overlaid on the game.
    Shows: score, coins, distance, speed, and active power-up.
    """
    hud_font  = pygame.font.SysFont("Verdana", 17, bold=True)
    tiny_font = pygame.font.SysFont("Verdana", 13)

    # Semi-transparent top bar background
    bar = pygame.Surface((SCREEN_WIDTH, 48), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 160))
    surface.blit(bar, (0, 0))

    # Left side: score and coins
    surface.blit(hud_font.render(f"Score  {state.score()}", True, ACCENT),  (8, 4))
    surface.blit(hud_font.render(f"Coins  {state.coin_count}", True, WHITE), (8, 26))

    # Centre: distance
    dist_lbl = hud_font.render(f"{state.metres()} m", True, GREEN)
    surface.blit(dist_lbl, dist_lbl.get_rect(centerx=SCREEN_WIDTH // 2, y=4))

    # Centre-bottom: difficulty label (small)
    diff_lbl = tiny_font.render(state.difficulty.upper(), True, (100, 100, 130))
    surface.blit(diff_lbl, diff_lbl.get_rect(centerx=SCREEN_WIDTH // 2, y=30))

    # Right side: speed
    spd_lbl = tiny_font.render(f"SPD {state.current_speed}", True, ORANGE)
    surface.blit(spd_lbl, spd_lbl.get_rect(right=SCREEN_WIDTH - 8, y=8))

    # Shield indicator
    if state.player.shield_active:
        sh_lbl = tiny_font.render("SHIELD", True, BLUE)
        surface.blit(sh_lbl, sh_lbl.get_rect(right=SCREEN_WIDTH - 8, y=28))

    # Active power-up indicator (bottom bar)
    if state.active_powerup_name:
        bottom_bar = pygame.Surface((SCREEN_WIDTH, 26), pygame.SRCALPHA)
        bottom_bar.fill((0, 0, 0, 140))
        surface.blit(bottom_bar, (0, SCREEN_HEIGHT - 26))

        secs = max(0, state.active_powerup_frames // 60)
        time_str = f"  {secs}s" if state.active_powerup_frames > 60 else ""
        pu_name  = state.active_powerup_name.upper()

        # Colour the label based on which power-up is active
        pu_color = {"Nitro": ORANGE, "Shield": BLUE, "Repair": GREEN}.get(
            state.active_powerup_name, WHITE)

        pu_lbl = hud_font.render(f"⚡ {pu_name}{time_str}", True, pu_color)
        surface.blit(pu_lbl, pu_lbl.get_rect(
            centerx=SCREEN_WIDTH // 2, y=SCREEN_HEIGHT - 24))
