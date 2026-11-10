from pathlib import Path

import psycopg

from app.config import ADMIN_DATABASE_URL


def main():
    with psycopg.connect(ADMIN_DATABASE_URL) as connection:
        available = connection.execute(
            "SELECT EXISTS (SELECT FROM pg_available_extensions WHERE name = 'vector')"
        ).fetchone()[0]
        if available:
            connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        schema = Path(__file__).resolve().parents[1] / "migrations/001_schema.sql"
        connection.execute(schema.read_text())
        if available:
            connection.execute(
                "ALTER TABLE help_faq ADD COLUMN IF NOT EXISTS embedding vector(64)"
            )
        print(f"Migration complete. pgvector={'enabled' if available else 'skipped'}")


if __name__ == "__main__":
    main()
