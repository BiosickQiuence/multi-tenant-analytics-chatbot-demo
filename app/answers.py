from app.router import QueryPlan


def summarize(plan: QueryPlan, rows: list[dict]) -> str:
    scope = f"{', '.join(plan.platforms)}, {plan.period}"
    if not rows:
        return f"No synthetic posts matched {scope}."
    first = rows[0]
    if plan.intent == "help":
        return " ".join(row["answer"] for row in rows)
    if plan.intent == "totals":
        summary = (f"{first['posts']} posts generated {first['engagements']:,} engagements "
                   f"and {first['impressions']:,} impressions. "
                   f"Engagement rate was {float(first['engagement_rate_pct']):.2f}%.")
    elif plan.intent in ("top_posts", "worst_posts"):
        summary = (f"Showing {len(rows)} {plan.intent.replace('_', ' ')} by total engagements. "
                   f"The first is on {first['platform']} with {first['engagements']:,} engagements.")
    elif plan.intent == "engagement_rate":
        summary = (f"{first['platform']} leads at {float(first['engagement_rate_pct']):.2f}% "
                   "engagement per impression, weighted across posts.")
    elif plan.intent == "follower_growth":
        summary = f"Posts were attributed {sum(row['followers_gained'] for row in rows):,} followers gained."
    elif plan.intent == "best_posting_time":
        summary = (f"{first['weekday']} at {first['hour_utc']:02d}:00 UTC had the highest mean "
                   f"engagements per post ({float(first['average_engagements']):.2f}), "
                   f"based on {first['posts']} posts in that time bucket.")
    else:
        summary = "Compared platforms. " + " ".join(
            f"{row['platform']} had {row['posts']} posts and "
            f"{float(row['engagement_rate_pct']):.2f}% engagement rate." for row in rows
        )
    return f"{summary} Scope is {scope}. Synthetic demo data."
