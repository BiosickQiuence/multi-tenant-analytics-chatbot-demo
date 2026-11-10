import random
from datetime import timedelta
from uuid import NAMESPACE_DNS, uuid5

import psycopg

from app.config import ADMIN_DATABASE_URL, DEMO_NOW
from app.embedding import hash_embedding, vector_literal

TENANTS = [
    ("Acme Coffee", "acme", "demo_acme_local_only"),
    ("Bluebird Fitness", "bluebird", "demo_bluebird_local_only"),
    ("Nova Books", "nova", "demo_nova_local_only"),
]
PLATFORMS = ("instagram", "tiktok", "x")
FAQ = [
    (
        "What can you answer? Help capabilities analytics",
        "I can report totals, top posts, worst posts, engagement rates, follower "
        "growth, best posting times, and comparisons between two platforms. "
        "Try last 7 days, last month, or this week. All data is synthetic.",
    ),
    (
        "How is engagement rate calculated? Formula impressions",
        "Engagement rate is 100 * (likes + comments + shares) / impressions, "
        "aggregated over the selected posts. Followers gained is a synthetic "
        "per-post attribution metric.",
    ),
    (
        "Are my tenant data and sessions isolated? Security privacy",
        "API keys determine the tenant. Repository filters and PostgreSQL "
        "row-level security isolate posts, FAQ entries, and chat history.",
    ),
]


def stable_id(label: str):
    return uuid5(NAMESPACE_DNS, f"tenant-chatbot-synthetic/{label}")


def main():
    rng = random.Random(20261110)
    with psycopg.connect(ADMIN_DATABASE_URL) as connection:
        has_vector = connection.execute(
            "SELECT EXISTS (SELECT FROM pg_extension WHERE extname = 'vector')"
        ).fetchone()[0]
        # Reruns restore the same synthetic fixtures without discarding chat history.
        for tenant_number, (name, slug, api_key) in enumerate(TENANTS):
            tenant_id = stable_id(slug)
            connection.execute(
                "INSERT INTO tenants (tenant_id, name) VALUES (%s, %s) "
                "ON CONFLICT (tenant_id) DO UPDATE SET name = EXCLUDED.name",
                (tenant_id, name),
            )
            connection.execute(
                "INSERT INTO users (id, tenant_id, name, api_key) VALUES (%s,%s,%s,%s) "
                "ON CONFLICT (id) DO UPDATE SET api_key = EXCLUDED.api_key",
                (stable_id(f"{slug}/user"), tenant_id, f"{name} Demo Analyst", api_key),
            )
            for platform in PLATFORMS:
                account_id = stable_id(f"{slug}/{platform}")
                connection.execute(
                    "INSERT INTO social_accounts (id, tenant_id, platform, handle) "
                    "VALUES (%s,%s,%s,%s) ON CONFLICT (id) DO NOTHING",
                    (account_id, tenant_id, platform, f"synthetic_{slug}"),
                )
                for day in range(90):
                    posted_at = (DEMO_NOW.replace(hour=0) - timedelta(days=90 - day)).replace(
                        hour=(8 + day * 3 + PLATFORMS.index(platform) * 4) % 24
                    )
                    likes = rng.randint(15, 600) + tenant_number * 100
                    comments = rng.randint(1, 65)
                    shares = rng.randint(0, 90)
                    impressions = (likes + comments + shares) * rng.randint(8, 30)
                    connection.execute(
                        "INSERT INTO posts (id, tenant_id, social_account_id, platform, "
                        "posted_at, likes, comments, shares, impressions, followers_gained, caption) "
                        "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) "
                        "ON CONFLICT (id) DO UPDATE SET posted_at=EXCLUDED.posted_at, "
                        "likes=EXCLUDED.likes, comments=EXCLUDED.comments, shares=EXCLUDED.shares, "
                        "impressions=EXCLUDED.impressions, followers_gained=EXCLUDED.followers_gained, "
                        "caption=EXCLUDED.caption",
                        (stable_id(f"{slug}/{platform}/{day}"), tenant_id, account_id,
                         platform, posted_at, likes, comments, shares, impressions,
                         rng.randint(0, 35), f"[SYNTHETIC] {name} {platform} post {day + 1}"),
                    )
            for index, (question, answer) in enumerate(FAQ):
                faq_id = stable_id(f"{slug}/faq/{index}")
                connection.execute(
                    "INSERT INTO help_faq (id, tenant_id, question, answer) VALUES (%s,%s,%s,%s) "
                    "ON CONFLICT (id) DO UPDATE SET question=EXCLUDED.question, answer=EXCLUDED.answer",
                    (faq_id, tenant_id, question, answer),
                )
                if has_vector:
                    connection.execute(
                        "UPDATE help_faq SET embedding = %s::vector WHERE id = %s",
                        (vector_literal(hash_embedding(question)), faq_id),
                    )
            print(f"{name}: 270 synthetic posts, 3 accounts, 3 FAQ entries")
    print(f"Fixed demo clock: {DEMO_NOW.isoformat()}; 90 complete UTC days before it.")


if __name__ == "__main__":
    main()
