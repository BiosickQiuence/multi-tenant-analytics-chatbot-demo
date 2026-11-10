DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'tenant_chatbot_app') THEN
        CREATE ROLE tenant_chatbot_app LOGIN PASSWORD 'local_app_demo'
            NOSUPERUSER NOCREATEDB NOCREATEROLE NOINHERIT NOBYPASSRLS;
    END IF;
END $$;

REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO tenant_chatbot_app;

CREATE TABLE IF NOT EXISTS tenants (
    tenant_id uuid PRIMARY KEY,
    name text NOT NULL,
    synthetic boolean NOT NULL DEFAULT true CHECK (synthetic)
);
CREATE TABLE IF NOT EXISTS users (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(tenant_id),
    name text NOT NULL,
    api_key text NOT NULL UNIQUE,
    UNIQUE (tenant_id, id)
);
CREATE TABLE IF NOT EXISTS social_accounts (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(tenant_id),
    platform text NOT NULL CHECK (platform IN ('instagram', 'tiktok', 'x')),
    handle text NOT NULL,
    UNIQUE (tenant_id, id),
    UNIQUE (tenant_id, platform)
);
CREATE TABLE IF NOT EXISTS posts (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(tenant_id),
    social_account_id uuid NOT NULL,
    platform text NOT NULL CHECK (platform IN ('instagram', 'tiktok', 'x')),
    posted_at timestamptz NOT NULL,
    likes integer NOT NULL CHECK (likes >= 0),
    comments integer NOT NULL CHECK (comments >= 0),
    shares integer NOT NULL CHECK (shares >= 0),
    impressions integer NOT NULL CHECK (impressions > 0),
    followers_gained integer NOT NULL CHECK (followers_gained >= 0),
    caption text NOT NULL,
    FOREIGN KEY (tenant_id, social_account_id)
        REFERENCES social_accounts(tenant_id, id)
);
CREATE INDEX IF NOT EXISTS posts_tenant_date ON posts(tenant_id, posted_at);
CREATE TABLE IF NOT EXISTS chat_sessions (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(tenant_id),
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    last_context jsonb NOT NULL DEFAULT '{}',
    UNIQUE (tenant_id, id)
);
CREATE TABLE IF NOT EXISTS chat_messages (
    id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(tenant_id),
    session_id uuid NOT NULL,
    role text NOT NULL CHECK (role IN ('user', 'assistant')),
    content text NOT NULL,
    intent text,
    template text,
    rows jsonb,
    created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
    FOREIGN KEY (tenant_id, session_id) REFERENCES chat_sessions(tenant_id, id)
);
CREATE INDEX IF NOT EXISTS messages_tenant_session
    ON chat_messages(tenant_id, session_id, id);
CREATE TABLE IF NOT EXISTS help_faq (
    id uuid PRIMARY KEY,
    tenant_id uuid NOT NULL REFERENCES tenants(tenant_id),
    question text NOT NULL,
    answer text NOT NULL
);

DO $$
DECLARE table_name text;
BEGIN
    FOREACH table_name IN ARRAY ARRAY[
        'tenants', 'users', 'social_accounts', 'posts',
        'chat_sessions', 'chat_messages', 'help_faq'
    ] LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY', table_name);
        EXECUTE format('ALTER TABLE %I FORCE ROW LEVEL SECURITY', table_name);
        EXECUTE format('DROP POLICY IF EXISTS tenant_boundary ON %I', table_name);
        EXECUTE format(
            'CREATE POLICY tenant_boundary ON %I USING '
            '(tenant_id = NULLIF(current_setting(''app.tenant_id'', true), '''')::uuid) '
            'WITH CHECK '
            '(tenant_id = NULLIF(current_setting(''app.tenant_id'', true), '''')::uuid)',
            table_name
        );
    END LOOP;
END $$;

GRANT SELECT ON tenants, users, social_accounts, posts, help_faq TO tenant_chatbot_app;
GRANT SELECT, INSERT, UPDATE ON chat_sessions TO tenant_chatbot_app;
GRANT SELECT, INSERT ON chat_messages TO tenant_chatbot_app;
GRANT USAGE ON SEQUENCE chat_messages_id_seq TO tenant_chatbot_app;

-- The sole pre-tenant lookup. No direct user-table access bypass is granted.
CREATE SCHEMA IF NOT EXISTS auth;
REVOKE ALL ON SCHEMA auth FROM PUBLIC;
GRANT USAGE ON SCHEMA auth TO tenant_chatbot_app;
CREATE OR REPLACE FUNCTION auth.resolve_api_key(p_api_key text)
RETURNS TABLE (tenant_id uuid, user_id uuid)
LANGUAGE sql STABLE SECURITY DEFINER SET search_path = pg_catalog
AS $$ SELECT tenant_id, id FROM public.users WHERE api_key = p_api_key $$;
REVOKE ALL ON FUNCTION auth.resolve_api_key(text) FROM PUBLIC;
GRANT EXECUTE ON FUNCTION auth.resolve_api_key(text) TO tenant_chatbot_app;
