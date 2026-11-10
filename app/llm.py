"""Optional interface only. No SDK, credential reads, or network calls."""
import os
from typing import Protocol


class LLM(Protocol):
    def complete(self, prompt: str) -> str | None: ...


class NoopLLM:
    def complete(self, prompt: str) -> None:
        return None


class OpenAICompatibleLLM:
    """Future endpoint adapter stub. Intentionally has no HTTP implementation."""

    def __init__(self, base_url: str, model: str):
        self.base_url = base_url
        self.model = model

    def complete(self, prompt: str) -> str:
        raise NotImplementedError("Endpoint adapter is a stub. Demo uses rule-based SQL only.")


def get_llm() -> LLM:
    if os.getenv("LLM_ENABLED", "false").lower() == "true":
        return OpenAICompatibleLLM(
            os.getenv("LLM_BASE_URL", "http://127.0.0.1:11434/v1"),
            os.getenv("LLM_MODEL", "local-model"),
        )
    return NoopLLM()
