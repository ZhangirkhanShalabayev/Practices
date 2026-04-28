# db.py — database helpers using psycopg2

import psycopg2
from config import DB_CONFIG

# ─────────────────────────────────────────
def get_conn():
    return psycopg2.connect(**DB_CONFIG)

# ─────────────────────────────────────────
def init_db():
    """Create tables if they don't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER   NOT NULL,
        level_reached INTEGER   NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    );
    """
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()
    conn.close()

# ─────────────────────────────────────────
def get_or_create_player(username: str) -> int:
    """Return player id, inserting if needed."""
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    row = cur.fetchone()
    if row:
        pid = row[0]
    else:
        cur.execute(
            "INSERT INTO players (username) VALUES (%s) RETURNING id",
            (username,)
        )
        pid = cur.fetchone()[0]
        conn.commit()
    cur.close()
    conn.close()
    return pid

# ─────────────────────────────────────────
def save_session(username: str, score: int, level: int):
    """Save a finished game session."""
    conn = get_conn()
    cur  = conn.cursor()
    pid  = get_or_create_player(username)
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (pid, score, level)
    )
    conn.commit()
    cur.close()
    conn.close()

# ─────────────────────────────────────────
def get_personal_best(username: str) -> int:
    """Return highest score for this player, or 0."""
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT COALESCE(MAX(gs.score), 0)
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        WHERE p.username = %s
    """, (username,))
    best = cur.fetchone()[0]
    cur.close()
    conn.close()
    return best

# ─────────────────────────────────────────
def get_leaderboard(limit: int = 10):
    """Return top scores: list of (rank, username, score, level, date)."""
    conn = get_conn()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached,
               TO_CHAR(gs.played_at, 'YYYY-MM-DD') AS day
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT %s
    """, (limit,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [(i+1, r[0], r[1], r[2], r[3]) for i, r in enumerate(rows)]
