from contextlib import contextmanager
from uuid import UUID

from psycopg import sql
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from app.config import DATABASE_URL


def create_pool() -> ConnectionPool:
    return ConnectionPool(
        DATABASE_URL, min_size=1, max_size=8, open=False,
        kwargs={"row_factory": dict_row, "options": "-c timezone=UTC"},
    )


def database_status(pool: ConnectionPool) -> dict:
    with pool.connection() as connection:
        return connection.execute("""
            SELECT current_user AS database_role, rolsuper, rolbypassrls,
                   EXISTS (SELECT FROM pg_extension WHERE extname = 'vector') AS pgvector,
                   (SELECT COUNT(*) FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
                    WHERE n.nspname='public' AND c.relkind='r' AND
                    c.relname IN ('tenants','users','social_accounts','posts',
                                  'chat_sessions','chat_messages','help_faq')
                    AND c.relrowsecurity AND c.relforcerowsecurity) AS rls_tables,
                   EXISTS (SELECT FROM pg_tables WHERE schemaname='public'
                           AND tableowner=current_user) AS owns_tables
            FROM pg_roles WHERE rolname=current_user
        """).fetchone()


def authenticate(pool: ConnectionPool, api_key: str) -> dict | None:
    # This narrowly scoped SECURITY DEFINER function is the only pre-tenant lookup.
    with pool.connection() as connection:
        return connection.execute(
            "SELECT * FROM auth.resolve_api_key(%(api_key)s)", {"api_key": api_key}
        ).fetchone()


@contextmanager
def tenant_transaction(pool: ConnectionPool, tenant_id: UUID):
    tenant_id = UUID(str(tenant_id))
    with pool.connection() as connection, connection.transaction():
        # PostgreSQL SET cannot bind a parameter. UUID validation and psycopg's
        # Literal safely quote this transaction-local setting. Data SQL is bound.
        connection.execute(
            sql.SQL("SET LOCAL app.tenant_id = {}").format(sql.Literal(str(tenant_id)))
        )
        yield connection
