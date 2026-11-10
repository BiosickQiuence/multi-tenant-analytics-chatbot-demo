import os
from datetime import UTC, datetime


# A fixed clock makes both the synthetic data and relative-date answers repeatable.
DEMO_NOW = datetime(2026, 11, 10, 12, tzinfo=UTC)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://tenant_chatbot_app:local_app_demo@127.0.0.1:55432/tenant_chatbot",
)
ADMIN_DATABASE_URL = os.getenv(
    "DATABASE_ADMIN_URL",
    "postgresql://postgres:local_admin_demo@127.0.0.1:55432/tenant_chatbot",
)
