import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta

from app.config import DEMO_NOW

PLATFORMS = ("instagram", "tiktok", "x")
INTENTS = (
    ("help", r"\b(help|capabilities|what can you|how.*calculated|formula|privacy|isolated|security)\b"),
    ("worst_posts", r"\b(worst|lowest|bottom|poor)\b"),
    ("compare_platforms", r"\b(compare|comparison|versus|vs)\b"),
    ("best_posting_time", r"\b(weekday|hour|posting time|best.*time|best.*day)\b"),
    ("follower_growth", r"\bfollower(s| growth)?\b"),
    ("engagement_rate", r"\b(engagement rate|rates?)\b"),
    ("top_posts", r"\b(top|best|highest)\b"),
    ("totals", r"\b(total(s)?|summary|overview|impressions|how many)\b"),
)


@dataclass
class QueryPlan:
    intent: str
    platforms: list[str]
    start: str
    end: str
    period: str

    def context(self) -> dict:
        return asdict(self)


def parse_dates(message: str) -> tuple[datetime, datetime, str] | None:
    today = DEMO_NOW.replace(hour=0, minute=0, second=0, microsecond=0)
    last_days = re.search(r"\blast\s+(\d+)\s+days?\b", message)
    if last_days:
        days = int(last_days.group(1))
        if not 1 <= days <= 3660:
            raise ValueError("Use a date window between 1 and 3660 days.")
        return today - timedelta(days=days), today, f"last {days} complete days"
    if "last month" in message:
        end = today.replace(day=1)
        return (end - timedelta(days=1)).replace(day=1), end, "last calendar month"
    if "this week" in message:
        return today - timedelta(days=today.weekday()), DEMO_NOW, "this week to the demo clock"
    if "this month" in message:
        return today.replace(day=1), DEMO_NOW, "this month to the demo clock"
    if "all time" in message:
        return today - timedelta(days=90), DEMO_NOW, "all 90 synthetic days"
    explicit = re.search(r"\bfrom (\d{4}-\d{2}-\d{2}) to (\d{4}-\d{2}-\d{2})\b", message)
    if explicit:
        try:
            start, last = [datetime.fromisoformat(value).replace(tzinfo=DEMO_NOW.tzinfo)
                           for value in explicit.groups()]
        except ValueError as error:
            raise ValueError("Use valid calendar dates in YYYY-MM-DD form.") from error
        if start > last:
            raise ValueError("The start date must be on or before the end date.")
        return start, last + timedelta(days=1), f"{start.date()} through {last.date()} inclusive"
    return None


def route_question(message: str, previous: dict | None = None) -> QueryPlan:
    text = message.lower().strip()
    intent = next((name for name, pattern in INTENTS if re.search(pattern, text)), None)
    platforms = [name for name in PLATFORMS if re.search(rf"\b{name}\b", text)]
    dates = parse_dates(text)
    previous = previous or {}
    if intent is None:
        if not (platforms or dates) or not previous or previous.get("intent") == "help":
            raise ValueError("Ask for totals, top/worst posts, engagement rate, follower growth, "
                             "best posting time, a two-platform comparison, or help.")
        intent = previous["intent"]
    if not platforms:
        platforms = previous.get("platforms", list(PLATFORMS))
    if intent == "compare_platforms" and len(platforms) != 2:
        raise ValueError("Name exactly two platforms to compare, for example instagram and tiktok.")
    if dates:
        start, end, period = dates
    elif previous.get("start"):
        start, end = datetime.fromisoformat(previous["start"]), datetime.fromisoformat(previous["end"])
        period = previous["period"]
    else:
        start = DEMO_NOW.replace(hour=0) - timedelta(days=30)
        end = DEMO_NOW.replace(hour=0)
        period = "last 30 complete days"
    return QueryPlan(intent, platforms, start.isoformat(), end.isoformat(), period)
