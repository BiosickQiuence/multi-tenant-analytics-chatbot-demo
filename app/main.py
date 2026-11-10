from contextlib import asynccontextmanager
from typing import Annotated
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.answers import summarize
from app.config import DEMO_NOW
from app.db import authenticate, create_pool, database_status, tenant_transaction
from app.llm import get_llm
from app.repository import TenantRepository
from app.router import route_question


@asynccontextmanager
async def lifespan(application: FastAPI):
    pool = create_pool()
    application.state.pool = pool
    try:
        pool.open(wait=True, timeout=15)
        status = database_status(pool)
        if status["rolsuper"] or status["rolbypassrls"] or status["owns_tables"] or status["rls_tables"] != 7:
            raise RuntimeError("App requires a non-owner, non-superuser, NOBYPASSRLS role and all 7 RLS tables.")
        application.state.pgvector = status["pgvector"]
        application.state.llm = get_llm()
        yield
    finally:
        pool.close()


app = FastAPI(
    title="Multi-tenant analytics chatbot",
    description="Personal portfolio demo by Zhuangyi Qiu. Rule-based intent router. "
                "Synthetic data. No LLM calls. Tenant isolation uses repository filters and PostgreSQL RLS.",
    version="1.0.0", lifespan=lifespan,
)
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


@app.middleware("http")
async def reject_tenant_query(request: Request, call_next):
    if "tenant_id" in request.query_params:
        return JSONResponse(status_code=422, content={"detail": "tenant_id is determined only by X-API-Key."})
    return await call_next(request)


def current_identity(request: Request, api_key: Annotated[str | None, Depends(api_key_header)]):
    identity = authenticate(request.app.state.pool, api_key) if api_key else None
    if identity is None:
        raise HTTPException(401, "Missing or unknown X-API-Key.")
    return identity


Identity = Annotated[dict, Depends(current_identity)]


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    session_id: UUID | None = None
    message: str = Field(min_length=1, max_length=2000, examples=["Top posts on instagram last 7 days"])

    @field_validator("message")
    @classmethod
    def nonblank_message(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Message must contain text.")
        return value.strip()


class ChatResponse(BaseModel):
    session_id: UUID
    answer: str
    intent: str
    template: str
    rows: list[dict]


@app.get("/health", tags=["Operations"])
def health(request: Request):
    status = database_status(request.app.state.pool)
    return {"status": "ok", "mode": "rule-based", "synthetic_data": True,
            "llm_calls": False, "demo_clock": DEMO_NOW.isoformat(), **status}


@app.post("/chat", response_model=ChatResponse, tags=["Analytics"])
def chat(payload: ChatRequest, request: Request, identity: Identity):
    tenant_id = identity["tenant_id"]
    with tenant_transaction(request.app.state.pool, tenant_id) as connection:
        repository = TenantRepository(connection, tenant_id)
        previous = {}
        if payload.session_id:
            session = repository.get_session(payload.session_id, lock=True)
            if session is None:
                raise HTTPException(404, "Session not found.")
            previous = session["last_context"]
        try:
            plan = route_question(payload.message, previous)
        except ValueError as error:
            raise HTTPException(422, str(error)) from error
        session_id = payload.session_id or repository.create_session()
        template, raw_rows = repository.answer_rows(plan, payload.message, request.app.state.pgvector)
        rows = jsonable_encoder(raw_rows)
        answer = summarize(plan, rows)
        repository.save_turn(session_id, payload.message, answer, plan, template, rows)
        return ChatResponse(session_id=session_id, answer=answer, intent=plan.intent,
                            template=template, rows=rows)


@app.get("/sessions/{session_id}", tags=["History"])
def session_history(session_id: UUID, request: Request, identity: Identity):
    with tenant_transaction(request.app.state.pool, identity["tenant_id"]) as connection:
        repository = TenantRepository(connection, identity["tenant_id"])
        session = repository.get_session(session_id)
        if session is None:
            raise HTTPException(404, "Session not found.")
        return {**session, "messages": repository.get_messages(session_id)}
