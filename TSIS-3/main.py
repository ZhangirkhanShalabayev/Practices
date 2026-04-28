"""
main.py
=======
Entry point for the TSIS 3 Racer Game.

How to run:
    python main.py

Program flow:
    1. Load saved settings and leaderboard from JSON files
    2. Show the Main Menu
    3. If Play: ask for a name, then run the game loop
    4. On Game Over: save the score, show the Game Over screen
    5. Player can Retry (go back to step 3) or return to Menu (step 2)
    6. Leaderboard and Settings are accessible from the Main Menu

File structure:
    main.py        ← you are here (entry point, game loop)
    racer.py       ← all game objects and logic
    ui.py          ← all screens and HUD drawing
    persistence.py ← save/load leaderboard.json and settings.json
    assets/        ← image files (player.png, enemy.png, coin*.png)
"""

import pygame
import sys

# Initialise pygame before importing any module that uses it
pygame.init()

from racer       import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GameState
from ui          import (main_menu, username_screen, settings_screen,
                         leaderboard_screen, game_over_screen, draw_hud)
from persistence import (load_settings, save_settings,
                         load_leaderboard, save_score)

# ===========================================================
# CREATE THE WINDOW
# ===========================================================
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer – TSIS 3")
clock  = pygame.time.Clock()


# ===========================================================
# MAIN FUNCTION
# ===========================================================
def main():
    """
    Top-level loop that handles screen navigation.
    Runs until the player quits.
    """

    # Load saved preferences and scores at startup
    settings = load_settings()
    username = "Player"          # default name until the player types one

    while True:

        # -------------------------------------------------------
        # MAIN MENU
        # -------------------------------------------------------
        choice = main_menu(screen, clock)

        if choice == "quit":
            pygame.quit()
            sys.exit()

        if choice == "leaderboard":
            leaderboard_screen(screen, clock, load_leaderboard())
            continue   # go back to main menu

        if choice == "settings":
            settings = settings_screen(screen, clock, settings)
            save_settings(settings)   # persist immediately
            continue

        # -------------------------------------------------------
        # PLAY — ask for a name then start the game
        # -------------------------------------------------------
        if choice == "play":
            username = username_screen(screen, clock, default=username)

            # This inner loop lets the player retry without re-entering
            # their name every time.
            while True:

                # Create a fresh GameState for this run
                state = GameState(
                    difficulty=settings["difficulty"],
                    car_color=settings["car_color"],
                )

                # ---------------------------------------------------
                # GAMEPLAY LOOP — runs at 60 FPS until game_over
                # ---------------------------------------------------
                while not state.game_over:
                    # Handle window close and pause (ESC)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            sys.exit()
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                state.game_over = True   # treat ESC as instant quit

                    state.update()          # update all game objects
                    state.draw(screen)      # draw road, cars, coins, etc.
                    draw_hud(screen, state, username)  # draw score overlay
                    pygame.display.flip()   # show the new frame
                    clock.tick(FPS)         # cap at 60 FPS

                # ---------------------------------------------------
                # GAME OVER — save score and show result screen
                # ---------------------------------------------------
                final_score    = state.score()
                final_distance = state.metres()
                final_coins    = state.coin_count

                save_score(username, final_score, final_distance, final_coins)

                result = game_over_screen(
                    screen, clock,
                    final_score, final_distance, final_coins, username
                )

                if result == "retry":
                    continue    # start a new run (stay in inner while loop)
                else:
                    break       # return to main menu (exit inner while loop)


# ===========================================================
# ENTRY POINT
# ===========================================================
if __name__ == "__main__":
    main()
