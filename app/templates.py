"""Only these fixed SQL strings may answer analytics questions."""

FILTERED_POSTS = """
WITH filtered AS (
    SELECT *, likes + comments + shares AS engagements
    FROM posts
    WHERE tenant_id = %(tenant_id)s
      AND posted_at >= %(start)s::timestamptz
      AND posted_at < %(end)s::timestamptz
      AND platform = ANY(%(platforms)s)
)
"""

METRICS = """
    COUNT(*)::integer AS posts,
    SUM(likes)::bigint AS likes,
    SUM(comments)::bigint AS comments,
    SUM(shares)::bigint AS shares,
    SUM(impressions)::bigint AS impressions,
    SUM(engagements)::bigint AS engagements,
    SUM(followers_gained)::bigint AS followers_gained,
    ROUND(100.0 * SUM(engagements) / NULLIF(SUM(impressions), 0), 2) AS engagement_rate_pct
"""

POST_COLUMNS = """
    tenant_id, id, platform, posted_at, caption, likes, comments, shares,
    impressions, engagements,
    ROUND(100.0 * engagements / NULLIF(impressions, 0), 2) AS engagement_rate_pct
"""

SQL_TEMPLATES = {
    "top_posts": FILTERED_POSTS + f"""
        SELECT {POST_COLUMNS} FROM filtered ORDER BY engagements DESC, id LIMIT 5
    """,
    "worst_posts": FILTERED_POSTS + f"""
        SELECT {POST_COLUMNS} FROM filtered ORDER BY engagements ASC, id LIMIT 5
    """,
    "engagement_rate": FILTERED_POSTS + f"""
        SELECT tenant_id, platform, {METRICS} FROM filtered
        GROUP BY tenant_id, platform ORDER BY engagement_rate_pct DESC, platform
    """,
    "totals": FILTERED_POSTS + f"""
        SELECT tenant_id, {METRICS} FROM filtered GROUP BY tenant_id
    """,
    "compare_platforms": FILTERED_POSTS + f"""
        SELECT tenant_id, platform, {METRICS} FROM filtered
        GROUP BY tenant_id, platform ORDER BY platform
    """,
    "follower_growth": FILTERED_POSTS + """
        SELECT tenant_id, platform, COUNT(*)::integer AS posts,
               SUM(followers_gained)::bigint AS followers_gained
        FROM filtered GROUP BY tenant_id, platform ORDER BY followers_gained DESC, platform
    """,
    "best_posting_time": FILTERED_POSTS + """
        SELECT tenant_id,
               EXTRACT(ISODOW FROM posted_at AT TIME ZONE 'UTC')::integer AS weekday_number,
               TO_CHAR(posted_at AT TIME ZONE 'UTC', 'FMDay') AS weekday,
               EXTRACT(HOUR FROM posted_at AT TIME ZONE 'UTC')::integer AS hour_utc,
               COUNT(*)::integer AS posts,
               ROUND(AVG(engagements), 2) AS average_engagements
        FROM filtered GROUP BY tenant_id, weekday_number, weekday, hour_utc
        ORDER BY average_engagements DESC, weekday_number, hour_utc LIMIT 5
    """,
}

FAQ_VECTOR_SQL = """
SELECT tenant_id, question, answer,
       (embedding <=> %(embedding)s::vector) AS cosine_distance
FROM help_faq WHERE tenant_id = %(tenant_id)s
ORDER BY embedding <=> %(embedding)s::vector, id LIMIT 1
"""

FAQ_FALLBACK_SQL = """
SELECT tenant_id, question, answer FROM help_faq
WHERE tenant_id = %(tenant_id)s ORDER BY id LIMIT 3
"""
