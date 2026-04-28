# config.py — central constants

WIDTH, HEIGHT = 800, 600
CELL_SIZE = 20
FPS = 60

# DB
DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "password": "12345678",
    "host": "localhost",
    "port": 5432,
}

# Colors
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
GRAY    = (40,  40,  40)
RED     = (200, 0,   0)
GREEN   = (0,   200, 0)
ORANGE  = (255, 165, 0)
YELLOW  = (255, 255, 0)
DARK_RED= (120, 0,   0)   # poison
BLUE    = (0,   120, 255) # speed boost
CYAN    = (0,   220, 220) # slow motion
PURPLE  = (160, 0,   200) # shield
BROWN   = (139, 90,  43)  # obstacle

FOOD_LIFETIME   = 5      # seconds normal food disappears
POWERUP_FIELD_DURATION = 8000  # ms before powerup disappears from field
POWERUP_EFFECT_DURATION= 5000  # ms effect lasts after collection
POISON_SHORTEN  = 2
OBSTACLES_START_LEVEL = 3
OBSTACLE_COUNT_PER_LEVEL = 5
