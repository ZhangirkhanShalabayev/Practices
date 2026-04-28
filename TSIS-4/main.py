# main.py — screens: Main Menu, Leaderboard, Settings, Game Over

import pygame
import json
import os
import sys

from config import *
import db
from game import run_game

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")


# ──────────────────────────────────────────────
#  Settings helpers
# ──────────────────────────────────────────────

def load_settings():
    try:
        with open(SETTINGS_FILE) as f:
            return json.load(f)
    except Exception:
        return {"snake_color": list(GREEN), "grid": True, "sound": False}


def save_settings(s):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(s, f, indent=4)


# ──────────────────────────────────────────────
#  Reusable UI helpers
# ──────────────────────────────────────────────

def draw_button(screen, font, text, rect, hovered):
    color = (80, 80, 200) if hovered else (50, 50, 150)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, WHITE, rect, 2, border_radius=8)
    lbl = font.render(text, True, WHITE)
    screen.blit(lbl, lbl.get_rect(center=rect.center))


def is_hovered(rect):
    return rect.collidepoint(pygame.mouse.get_pos())


# ──────────────────────────────────────────────
#  Username input screen
# ──────────────────────────────────────────────

def screen_username(screen, clock):
    font     = pygame.font.SysFont("arial", 32)
    big_font = pygame.font.SysFont("arial", 46)
    username = ""

    while True:
        screen.fill(BLACK)
        title = big_font.render("Enter Your Username", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 80)))

        # input box
        box = pygame.Rect(WIDTH//2 - 180, HEIGHT//2 - 25, 360, 50)
        pygame.draw.rect(screen, GRAY, box, border_radius=6)
        pygame.draw.rect(screen, WHITE, box, 2, border_radius=6)
        name_surf = font.render(username + "|", True, WHITE)
        screen.blit(name_surf, (box.x + 10, box.y + 10))

        hint = pygame.font.SysFont("arial", 22).render("Press ENTER to continue", True, GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and username.strip():
                    return username.strip()
                elif event.key == pygame.K_BACKSPACE:
                    username = username[:-1]
                elif event.unicode.isprintable() and len(username) < 20:
                    username += event.unicode


# ──────────────────────────────────────────────
#  Main Menu
# ──────────────────────────────────────────────

def screen_main_menu(screen, clock, username):
    font     = pygame.font.SysFont("arial", 30)
    big_font = pygame.font.SysFont("arial", 52)

    buttons = {
        "Play":        pygame.Rect(WIDTH//2 - 110, 200, 220, 55),
        "Leaderboard": pygame.Rect(WIDTH//2 - 110, 275, 220, 55),
        "Settings":    pygame.Rect(WIDTH//2 - 110, 350, 220, 55),
        "Quit":        pygame.Rect(WIDTH//2 - 110, 425, 220, 55),
    }

    while True:
        screen.fill(BLACK)
        title = big_font.render("🐍 SNAKE", True, GREEN)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 110)))

        sub = font.render(f"Player: {username}", True, GRAY)
        screen.blit(sub, sub.get_rect(center=(WIDTH//2, 160)))

        for label, rect in buttons.items():
            draw_button(screen, font, label, rect, is_hovered(rect))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for label, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return label  # "Play" | "Leaderboard" | "Settings" | "Quit"


# ──────────────────────────────────────────────
#  Game Over screen
# ──────────────────────────────────────────────

def screen_game_over(screen, clock, score, level, personal_best):
    font     = pygame.font.SysFont("arial", 28)
    big_font = pygame.font.SysFont("arial", 52)

    retry_btn = pygame.Rect(WIDTH//2 - 120, HEIGHT//2 + 60, 110, 50)
    menu_btn  = pygame.Rect(WIDTH//2 + 10,  HEIGHT//2 + 60, 110, 50)

    while True:
        screen.fill(BLACK)

        title = big_font.render("GAME OVER", True, RED)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 100)))

        for i, line in enumerate([
            f"Score: {score}",
            f"Level reached: {level}",
            f"Personal best: {personal_best}",
        ]):
            surf = font.render(line, True, WHITE)
            screen.blit(surf, surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 30 + i*36)))

        draw_button(screen, font, "Retry",     retry_btn, is_hovered(retry_btn))
        draw_button(screen, font, "Main Menu", menu_btn,  is_hovered(menu_btn))

        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if retry_btn.collidepoint(event.pos):
                    return "retry"
                if menu_btn.collidepoint(event.pos):
                    return "menu"


# ──────────────────────────────────────────────
#  Leaderboard screen
# ──────────────────────────────────────────────

def screen_leaderboard(screen, clock):
    font     = pygame.font.SysFont("arial", 24)
    big_font = pygame.font.SysFont("arial", 40)
    sm_font  = pygame.font.SysFont("arial", 20)
    back_btn = pygame.Rect(WIDTH//2 - 70, HEIGHT - 65, 140, 45)

    try:
        rows = db.get_leaderboard(10)
    except Exception as e:
        rows = []
        err  = str(e)
    else:
        err = None

    while True:
        screen.fill(BLACK)
        title = big_font.render("🏆 Leaderboard", True, YELLOW)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 40)))

        if err:
            msg = font.render(f"DB error: {err}", True, RED)
            screen.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
        else:
            headers = ["#", "Username", "Score", "Level", "Date"]
            cols    = [50, 130, 420, 510, 590]
            head_surf = [sm_font.render(h, True, ORANGE) for h in headers]
            for s, x in zip(head_surf, cols):
                screen.blit(s, (x, 85))
            pygame.draw.line(screen, GRAY, (40, 108), (760, 108), 1)

            for rank, uname, sc, lv, dt in rows:
                y = 115 + (rank - 1) * 38
                color = YELLOW if rank == 1 else WHITE
                for txt, x in zip(
                    [str(rank), uname, str(sc), str(lv), dt], cols
                ):
                    screen.blit(sm_font.render(txt, True, color), (x, y))

        draw_button(screen, font, "Back", back_btn, is_hovered(back_btn))
        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_btn.collidepoint(event.pos):
                    return


# ──────────────────────────────────────────────
#  Settings screen
# ──────────────────────────────────────────────

COLOR_OPTIONS = {
    "Green":  [0, 200, 0],
    "Blue":   [0, 120, 255],
    "White":  [230, 230, 230],
    "Orange": [255, 165, 0],
    "Purple": [160, 0, 200],
}

def screen_settings(screen, clock, settings):
    font     = pygame.font.SysFont("arial", 28)
    big_font = pygame.font.SysFont("arial", 40)

    save_btn = pygame.Rect(WIDTH//2 - 90, HEIGHT - 80, 180, 50)

    color_names = list(COLOR_OPTIONS.keys())

    # find current color index
    cur_color_idx = 0
    for i, (k, v) in enumerate(COLOR_OPTIONS.items()):
        if v == settings["snake_color"]:
            cur_color_idx = i

    grid_on  = settings["grid"]
    sound_on = settings["sound"]

    while True:
        screen.fill(BLACK)
        title = big_font.render("⚙ Settings", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, 45)))

        # ── Grid toggle ──
        grid_rect = pygame.Rect(WIDTH//2 + 40, 130, 130, 42)
        lbl = font.render("Grid overlay:", True, WHITE)
        screen.blit(lbl, (WIDTH//2 - 180, 138))
        draw_button(screen, font, "ON" if grid_on else "OFF", grid_rect, is_hovered(grid_rect))

        # ── Sound toggle ──
        sound_rect = pygame.Rect(WIDTH//2 + 40, 200, 130, 42)
        lbl2 = font.render("Sound:", True, WHITE)
        screen.blit(lbl2, (WIDTH//2 - 180, 208))
        draw_button(screen, font, "ON" if sound_on else "OFF", sound_rect, is_hovered(sound_rect))

        # ── Color picker ──
        lbl3 = font.render("Snake color:", True, WHITE)
        screen.blit(lbl3, (WIDTH//2 - 180, 278))

        prev_rect = pygame.Rect(WIDTH//2 + 40,  270, 42, 42)
        next_rect = pygame.Rect(WIDTH//2 + 170, 270, 42, 42)
        color_name = color_names[cur_color_idx]
        color_val  = COLOR_OPTIONS[color_name]

        draw_button(screen, font, "<", prev_rect, is_hovered(prev_rect))
        draw_button(screen, font, ">", next_rect, is_hovered(next_rect))
        pygame.draw.rect(screen, tuple(color_val), [WIDTH//2 + 90, 270, 72, 42], border_radius=6)
        pygame.draw.rect(screen, WHITE,            [WIDTH//2 + 90, 270, 72, 42], 2, border_radius=6)
        clbl = pygame.font.SysFont("arial", 18).render(color_name, True, WHITE)
        screen.blit(clbl, clbl.get_rect(center=(WIDTH//2 + 126, 340)))

        draw_button(screen, font, "Save & Back", save_btn, is_hovered(save_btn))
        pygame.display.update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if grid_rect.collidepoint(event.pos):
                    grid_on = not grid_on
                elif sound_rect.collidepoint(event.pos):
                    sound_on = not sound_on
                elif prev_rect.collidepoint(event.pos):
                    cur_color_idx = (cur_color_idx - 1) % len(color_names)
                elif next_rect.collidepoint(event.pos):
                    cur_color_idx = (cur_color_idx + 1) % len(color_names)
                elif save_btn.collidepoint(event.pos):
                    settings["grid"]        = grid_on
                    settings["sound"]       = sound_on
                    settings["snake_color"] = COLOR_OPTIONS[color_names[cur_color_idx]]
                    save_settings(settings)
                    return settings


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake — TSIS 4")
    clock  = pygame.time.Clock()

    # init DB
    try:
        db.init_db()
    except Exception as e:
        print(f"[WARNING] DB not available: {e}")

    settings = load_settings()

    # username once per session
    username = screen_username(screen, clock)

    # personal best
    try:
        personal_best = db.get_personal_best(username)
    except Exception:
        personal_best = 0

    while True:
        action = screen_main_menu(screen, clock, username)

        if action == "Quit":
            break

        elif action == "Leaderboard":
            screen_leaderboard(screen, clock)

        elif action == "Settings":
            settings = screen_settings(screen, clock, settings)

        elif action == "Play":
            while True:
                score, level = run_game(screen, clock, settings, username, personal_best)

                # save to DB
                try:
                    db.save_session(username, score, level)
                    personal_best = db.get_personal_best(username)
                except Exception as e:
                    print(f"[WARNING] Could not save to DB: {e}")

                result = screen_game_over(screen, clock, score, level, personal_best)
                if result == "retry":
                    continue
                else:
                    break

    pygame.quit()


if __name__ == "__main__":
    main()
