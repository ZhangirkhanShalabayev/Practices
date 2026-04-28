import psycopg2
from config import DB_CONFIG

def get_connection():
    """Establish and return a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def close_connection(conn):
    """Close a database connection."""
    if conn:
        conn.close()
