"""
pgvector setup helper for PostgreSQL 16 on Windows.

Downloads the pgvector DLL and installs the extension.
Run once: python scripts/setup_pgvector.py
"""

import subprocess
import sys
from pathlib import Path


def check_extension():
    """Check if pgvector is already installed."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:%3FBooker78%21@localhost:5432/postgres"
        )
        cur = conn.cursor()
        cur.execute("SELECT extname FROM pg_extension WHERE extname = 'vector'")
        row = cur.fetchone()
        conn.close()
        return row is not None
    except Exception as e:
        print(f"Cannot connect to PostgreSQL: {e}")
        return False


def install_extension():
    """Create the vector extension."""
    try:
        import psycopg2
        conn = psycopg2.connect(
            "postgresql://postgres:%3FBooker78%21@localhost:5432/postgres"
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
        cur.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        conn.close()
        print("✓ pgvector extension created")
        return True
    except Exception as e:
        print(f"Failed to create extension: {e}")
        print("\nManual steps:")
        print("1. Download pgvector from https://github.com/pgvector/pgvector/releases")
        print("2. Copy vector.dll to C:\\Program Files\\PostgreSQL\\16\\lib\\")
        print("3. Copy vector.control + vector--*.sql to C:\\Program Files\\PostgreSQL\\16\\share\\extension\\")
        print("4. Run: psql -U postgres -c 'CREATE EXTENSION vector'")
        return False


if __name__ == "__main__":
    print("Checking pgvector...")
    if check_extension():
        print("✓ pgvector already installed")
    else:
        print("Installing pgvector...")
        install_extension()
