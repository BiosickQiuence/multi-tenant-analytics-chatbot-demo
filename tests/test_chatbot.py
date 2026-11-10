from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from uuid import uuid4

import psycopg
import pytest
from psycopg import sql

from app.config import DATABASE_URL
from app.db import tenant_transaction
from app.embedding import hash_embedding
from app.llm import NoopLLM
from app.main import app
from app.repository import TenantRepository
from app.router import route_question
from app.seed import TENANTS, stable_id

ACME = {"X-API-Key": TENANTS[0][2]}
BLUEBIRD = {"X-API-Key": TENANTS[1][2]}
TABLES = ("tenants", "users", "social_accounts", "posts", "chat_sessions", "chat_messages", "help_faq")


def ask(client, message, headers=ACME, session_id=None):
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id
    response = client.post("/chat", headers=headers, json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def test_health_confirms_real_db_role_and_rls(client):
    response = client.get("/health")
    assert response.status_code == 200
    health = response.json()
    assert health["database_role"] == "tenant_chatbot_app"
    assert not health["rolsuper"] and not health["rolbypassrls"] and not health["owns_tables"]
    assert health["rls_tables"] == 7
    assert health["mode"] == "rule-based" and not health["llm_calls"]


@pytest.mark.parametrize("headers", [{}, {"X-API-Key": "unknown-local-demo-key"}])
def test_missing_or_unknown_key_is_401(client, headers):
    assert client.post("/chat", headers=headers, json={"message": "totals"}).status_code == 401
    assert client.get(f"/sessions/{uuid4()}", headers=headers).status_code == 401


@pytest.mark.parametrize("name,slug,key", TENANTS, ids=["acme", "bluebird", "nova"])
def test_answers_only_include_authenticated_tenant(client, name, slug, key):
    response = ask(client, "top posts all time", {"X-API-Key": key})
    assert len(response["rows"]) == 5
    assert all(row["tenant_id"] == str(stable_id(slug)) for row in response["rows"])
    assert all(name in row["caption"] and "[SYNTHETIC]" in row["caption"] for row in response["rows"])
    totals = ask(client, "totals all time", {"X-API-Key": key})
    assert totals["rows"][0]["posts"] == 270


def test_cross_tenant_session_read_and_reuse_are_404(client):
    session = ask(client, "totals last 7 days", BLUEBIRD)["session_id"]
    assert client.get(f"/sessions/{session}", headers=ACME).status_code == 404
    response = client.post("/chat", headers=ACME,
                           json={"session_id": session, "message": "what about tiktok?"})
    assert response.status_code == 404
    history = client.get(f"/sessions/{session}", headers=BLUEBIRD).json()
    assert len(history["messages"]) == 2


def test_followups_keep_intent_and_unspecified_filters(client):
    first = ask(client, "top posts on instagram last 7 days")
    second = ask(client, "what about tiktok?", session_id=first["session_id"])
    third = ask(client, "and last month?", session_id=first["session_id"])
    assert first["session_id"] == second["session_id"] == third["session_id"]
    assert second["intent"] == third["intent"] == "top_posts"
    assert all(row["platform"] == "tiktok" for row in second["rows"] + third["rows"])
    assert all("2026-11-03" <= row["posted_at"] < "2026-11-10" for row in second["rows"])
    assert all("2026-10-01" <= row["posted_at"] < "2026-11-01" for row in third["rows"])
    history = client.get(f"/sessions/{first['session_id']}", headers=ACME).json()
    assert len(history["messages"]) == 6
    assert [entry["role"] for entry in history["messages"]] == ["user", "assistant"] * 3
    assert history["last_context"]["platforms"] == ["tiktok"]
    assert history["messages"][-1]["rows"] == third["rows"]


def test_new_sessions_have_independent_memory(client):
    ask(client, "top posts instagram last 7 days")
    fresh = ask(client, "totals last month")
    assert fresh["rows"][0]["posts"] == 31 * 3
    assert client.post("/chat", headers=ACME,
                       json={"message": "what about tiktok?"}).status_code == 422


def test_concurrent_turns_preserve_complete_session_history(client):
    session_id = ask(client, "totals last 7 days")["session_id"]
    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(
            lambda platform: ask(client, f"what about {platform}?", session_id=session_id),
            ["instagram", "tiktok", "x"],
        ))
    assert all(result["rows"][0]["posts"] == 7 for result in results)
    history = client.get(f"/sessions/{session_id}", headers=ACME).json()
    assert len(history["messages"]) == 8
    assert [entry["role"] for entry in history["messages"]] == ["user", "assistant"] * 4


@pytest.mark.parametrize("question,intent,columns", [
    ("top posts last 7 days", "top_posts", {"caption", "engagements", "posted_at"}),
    ("worst posts last month", "worst_posts", {"caption", "engagements", "posted_at"}),
    ("engagement rate by platform last 7 days", "engagement_rate", {"platform", "engagement_rate_pct"}),
    ("follower growth this week", "follower_growth", {"platform", "followers_gained", "posts"}),
    ("best posting weekday and hour last month", "best_posting_time", {"weekday", "hour_utc", "average_engagements"}),
    ("totals last 7 days", "totals", {"posts", "impressions", "engagements"}),
    ("compare instagram vs tiktok last month", "compare_platforms", {"platform", "posts", "engagement_rate_pct"}),
    ("what can you answer?", "help", {"question", "answer"}),
], ids=["top_posts", "worst_posts", "engagement_rate", "follower_growth", "best_posting_time",
        "totals", "compare_platforms", "help_faq"])
def test_each_whitelisted_template_has_expected_shape(client, question, intent, columns):
    response = ask(client, question)
    assert set(response) == {"session_id", "answer", "intent", "template", "rows"}
    assert response["intent"] == intent
    assert response["template"] == ("help_faq" if intent == "help" else intent)
    assert response["rows"] and response["answer"]
    for row in response["rows"]:
        assert columns <= row.keys()
        assert row["tenant_id"] == str(stable_id("acme"))


def test_totals_and_rates_are_internally_consistent(client):
    totals = ask(client, "totals last 7 days")["rows"][0]
    by_platform = ask(client, "engagement rate last 7 days")["rows"]
    assert totals["posts"] == 21
    assert totals["engagements"] == totals["likes"] + totals["comments"] + totals["shares"]
    for metric in ("posts", "likes", "comments", "shares", "impressions", "engagements", "followers_gained"):
        assert totals[metric] == sum(row[metric] for row in by_platform)
    assert totals["engagement_rate_pct"] == round(100 * totals["engagements"] / totals["impressions"], 2)


def test_ranked_posts_and_comparison_match_request(client):
    top = ask(client, "top posts last month")["rows"]
    worst = ask(client, "worst posts last month")["rows"]
    assert [row["engagements"] for row in top] == sorted((row["engagements"] for row in top), reverse=True)
    assert [row["engagements"] for row in worst] == sorted(row["engagements"] for row in worst)
    comparison = ask(client, "compare instagram and tiktok last 7 days")["rows"]
    assert {row["platform"] for row in comparison} == {"instagram", "tiktok"}
    assert all(row["posts"] == 7 for row in comparison)


def test_raw_queries_without_tenant_return_zero_for_every_data_table(client):
    with psycopg.connect(DATABASE_URL) as connection:
        for table in TABLES:
            count = connection.execute(sql.SQL("SELECT COUNT(*) FROM {}").format(sql.Identifier(table))).fetchone()[0]
            assert count == 0, table


def test_rls_rejects_wrong_repository_scope_and_unfiltered_sql(client):
    with tenant_transaction(app.state.pool, stable_id("acme")) as connection:
        raw = connection.execute("SELECT DISTINCT tenant_id FROM posts").fetchall()
        assert {row["tenant_id"] for row in raw} == {stable_id("acme")}
        repository = TenantRepository(connection, stable_id("bluebird"))
        _, rows = repository.answer_rows(route_question("totals all time"), "totals", app.state.pgvector)
        assert rows == []


def test_rls_with_check_rejects_cross_tenant_write(client):
    with pytest.raises(psycopg.errors.InsufficientPrivilege):
        with tenant_transaction(app.state.pool, stable_id("acme")) as connection:
            connection.execute("INSERT INTO chat_sessions (id, tenant_id) VALUES (%s,%s)",
                               (uuid4(), stable_id("bluebird")))


def test_set_local_resets_after_commit_and_rollback(client):
    with psycopg.connect(DATABASE_URL) as connection:
        with connection.transaction():
            connection.execute(sql.SQL("SET LOCAL app.tenant_id = {}").format(sql.Literal(str(stable_id("acme")))))
            assert connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0] == 270
        assert connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0] == 0
        connection.commit()
        with pytest.raises(RuntimeError):
            with connection.transaction():
                connection.execute(sql.SQL("SET LOCAL app.tenant_id = {}").format(sql.Literal(str(stable_id("bluebird")))))
                raise RuntimeError("exercise rollback")
        assert connection.execute("SELECT COUNT(*) FROM posts").fetchone()[0] == 0
    # Requests also return pooled connections with no tenant context retained.
    ask(client, "totals")
    with app.state.pool.connection() as connection:
        assert connection.execute("SELECT COUNT(*) AS count FROM posts").fetchone()["count"] == 0


@pytest.mark.parametrize("location", ["body", "query"])
def test_caller_cannot_supply_tenant_id(client, location):
    payload = {"message": "totals"}
    url = "/chat"
    if location == "body":
        payload["tenant_id"] = str(stable_id("bluebird"))
    else:
        url += f"?tenant_id={stable_id('bluebird')}"
    assert client.post(url, headers=ACME, json=payload).status_code == 422


@pytest.mark.parametrize("message", [" ", "unrecognized request", "totals last 0 days",
                                          "totals from 2026-02-30 to 2026-03-01"])
def test_invalid_or_unsupported_questions_are_422(client, message):
    assert client.post("/chat", headers=ACME, json={"message": message}).status_code == 422


def test_sql_like_text_cannot_execute_statements(client):
    response = ask(client, "totals last 7 days; DROP TABLE posts; --")
    assert response["template"] == "totals" and response["rows"][0]["posts"] == 21
    assert ask(client, "totals all time")["rows"][0]["posts"] == 270


@pytest.mark.parametrize("question,start,end", [
    ("totals last 7 days", "2026-11-03", "2026-11-10"),
    ("totals last month", "2026-10-01", "2026-11-01"),
    ("totals this week", "2026-11-09", "2026-11-10"),
    ("totals from 2026-10-01 to 2026-10-02", "2026-10-01", "2026-10-03"),
])
def test_relative_and_explicit_date_boundaries(question, start, end):
    plan = route_question(question)
    assert datetime.fromisoformat(plan.start).date().isoformat() == start
    assert datetime.fromisoformat(plan.end).date().isoformat() == end


def test_help_uses_local_hashing_and_real_vector_distance_when_available(client):
    vector = hash_embedding("what can you answer?")
    assert vector == hash_embedding("what can you answer?")
    assert len(vector) == 64 and sum(value * value for value in vector) == pytest.approx(1)
    response = ask(client, "what can you answer?")
    assert "totals" in response["answer"].lower()
    if app.state.pgvector:
        assert len(response["rows"]) == 1
        assert 0 <= response["rows"][0]["cosine_distance"] <= 2


def test_llm_default_is_noop_and_not_called(client, monkeypatch):
    assert isinstance(app.state.llm, NoopLLM)
    def forbidden_call(prompt):
        raise AssertionError("No LLM calls are permitted in demo mode")
    monkeypatch.setattr(app.state.llm, "complete", forbidden_call)
    assert ask(client, "totals last 7 days")["intent"] == "totals"
