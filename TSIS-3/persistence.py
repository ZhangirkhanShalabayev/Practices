"""
persistence.py
==============
Handles saving and loading game data between sessions.

Two files are managed:
  leaderboard.json  - top 10 player scores
  settings.json     - player preferences (sound, car colour, difficulty)

All functions use JSON so the files are human-readable.
"""

import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

# Default values used when settings.json does not yet exist
DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "blue",    # "blue" or "red"
    "difficulty": "normal",  # "easy", "normal", or "hard"
}


# ===========================================================
# LEADERBOARD
# ===========================================================

def load_leaderboard() -> list:
    """
    Load scores from leaderboard.json.
    Returns a list of dicts sorted by score (highest first),
    limited to the top 10.
    Returns an empty list if the file does not exist.
    """
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    try:
        with open(LEADERBOARD_FILE, "r") as f:
            data = json.load(f)
        data.sort(key=lambda entry: entry.get("score", 0), reverse=True)
        return data[:10]
    except (json.JSONDecodeError, Exception):
        return []   # if the file is corrupted, start fresh


def save_score(username: str, score: int, distance: int, coins: int):
    """
    Add a new entry to leaderboard.json, then keep only the top 10.

    Args:
        username : the player's name (entered on the name screen)
        score    : final score (coins + distance bonus)
        distance : metres driven
        coins    : coins collected
    """
    entries = load_leaderboard()

    # Add the new score
    entries.append({
        "name":     username,
        "score":    score,
        "distance": distance,
        "coins":    coins,
    })

    # Keep only the highest 10 scores
    entries.sort(key=lambda entry: entry.get("score", 0), reverse=True)
    entries = entries[:10]

    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(entries, f, indent=2)


# ===========================================================
# SETTINGS
# ===========================================================

def load_settings() -> dict:
    """
    Load settings from settings.json.
    If the file is missing or invalid, return the default settings.
    Any keys missing from the file are filled in from defaults,
    so adding new settings in future won't break old save files.
    """
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
        # Merge: start from defaults, then overwrite with saved values
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data)
        return merged
    except (json.JSONDecodeError, Exception):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict):
    """
    Write the settings dict to settings.json.
    Called every time the player clicks 'Save' in the Settings screen.
    """
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)
