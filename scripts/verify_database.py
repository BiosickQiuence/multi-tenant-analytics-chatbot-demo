"""Read-only administrative acceptance evidence for this demo database."""
import hashlib
import json
import sys
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import ADMIN_DATABASE_URL


def main():
    with psycopg.connect(ADMIN_DATABASE_URL, row_factory=dict_row) as connection:
        tenants = connection.execute("""
            SELECT t.name, p.tenant_id, COUNT(*) AS posts,
                   COUNT(DISTINCT platform) AS platforms, COUNT(DISTINCT posted_at::date) AS days,
                   MIN(posted_at) AS first_post, MAX(posted_at) AS last_post
            FROM posts p JOIN tenants t ON p.tenant_id=t.tenant_id
            GROUP BY t.name, p.tenant_id ORDER BY t.name
        """).fetchall()
        role = connection.execute("""
            SELECT rolname, rolsuper, rolbypassrls, rolcreatedb, rolcreaterole
            FROM pg_roles WHERE rolname='tenant_chatbot_app'
        """).fetchone()
        policies = connection.execute("""
            SELECT tablename, policyname, qual, with_check FROM pg_policies
            WHERE schemaname='public' ORDER BY tablename
        """).fetchall()
        vectors = connection.execute("""
            SELECT extversion FROM pg_extension WHERE extname='vector'
        """).fetchone()
        rows = connection.execute("""
            SELECT id, tenant_id, platform, posted_at, likes, comments, shares,
                   impressions, followers_gained, caption FROM posts ORDER BY id
        """).fetchall()
        assert len(tenants) == 3 and all(row["posts"] == 270 and row["days"] == 90 for row in tenants)
        assert len(policies) == 7
        assert not role["rolsuper"] and not role["rolbypassrls"]
        evidence = {"tenants": tenants, "app_role": role, "rls_policies": policies,
                    "pgvector": vectors, "post_count": len(rows),
                    "posts_sha256": hashlib.sha256(json.dumps(rows, default=str, sort_keys=True).encode()).hexdigest()}
    print(json.dumps(evidence, indent=2, default=str))


if __name__ == "__main__":
    main()
