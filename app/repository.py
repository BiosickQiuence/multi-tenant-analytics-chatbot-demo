from uuid import UUID, uuid4

from psycopg.types.json import Jsonb

from app.embedding import hash_embedding, vector_literal
from app.router import QueryPlan
from app.templates import FAQ_FALLBACK_SQL, FAQ_VECTOR_SQL, SQL_TEMPLATES


class TenantRepository:
    def __init__(self, connection, tenant_id: UUID):
        self.connection = connection
        self.tenant_id = UUID(str(tenant_id))

    def get_session(self, session_id: UUID, *, lock: bool = False) -> dict | None:
        query = """
            SELECT id, tenant_id, created_at, last_context FROM chat_sessions
            WHERE tenant_id = %(tenant_id)s AND id = %(session_id)s
        """
        if lock:
            query += " FOR UPDATE"
        return self.connection.execute(
            query, {"tenant_id": self.tenant_id, "session_id": session_id}
        ).fetchone()

    def create_session(self) -> UUID:
        session_id = uuid4()
        self.connection.execute(
            "INSERT INTO chat_sessions (id, tenant_id) VALUES (%(id)s, %(tenant_id)s)",
            {"id": session_id, "tenant_id": self.tenant_id},
        )
        return session_id

    def get_messages(self, session_id: UUID) -> list[dict]:
        return self.connection.execute(
            """SELECT role, content, intent, template, rows, created_at FROM chat_messages
               WHERE tenant_id = %(tenant_id)s AND session_id = %(session_id)s ORDER BY id""",
            {"tenant_id": self.tenant_id, "session_id": session_id},
        ).fetchall()

    def answer_rows(self, plan: QueryPlan, message: str, has_vector: bool) -> tuple[str, list[dict]]:
        parameters = {**plan.context(), "tenant_id": self.tenant_id}
        if plan.intent == "help":
            parameters["embedding"] = vector_literal(hash_embedding(message))
            query = FAQ_VECTOR_SQL if has_vector else FAQ_FALLBACK_SQL
            return "help_faq", self.connection.execute(query, parameters).fetchall()
        return plan.intent, self.connection.execute(SQL_TEMPLATES[plan.intent], parameters).fetchall()

    def save_turn(self, session_id: UUID, message: str, answer: str, plan: QueryPlan,
                  template: str, rows: list[dict]):
        for role, content in (("user", message), ("assistant", answer)):
            self.connection.execute(
                """INSERT INTO chat_messages
                   (tenant_id, session_id, role, content, intent, template, rows)
                   VALUES (%(tenant_id)s,%(session_id)s,%(role)s,%(content)s,
                           %(intent)s,%(template)s,%(rows)s)""",
                {"tenant_id": self.tenant_id, "session_id": session_id, "role": role,
                 "content": content, "intent": plan.intent, "template": template,
                 "rows": Jsonb(rows if role == "assistant" else [])},
            )
        self.connection.execute(
            """UPDATE chat_sessions SET last_context = %(context)s
               WHERE tenant_id = %(tenant_id)s AND id = %(session_id)s""",
            {"context": Jsonb(plan.context()), "tenant_id": self.tenant_id, "session_id": session_id},
        )
