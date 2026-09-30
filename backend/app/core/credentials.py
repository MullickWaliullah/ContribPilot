from __future__ import annotations

from dataclasses import dataclass

from fastapi import Header

from app.ai.llm_client import LLMAuthError
from app.core.config import settings


@dataclass(frozen=True, repr=False)
class UserCredentials:
    groq_api_key: str
    github_token: str | None = None

    def __repr__(self) -> str:
        return "UserCredentials(groq_api_key=***, github_token=***)"


def _clean(value: str | None) -> str | None:
    if value is None:
        return None

    value = value.strip()

    return value or None


def get_credentials(
    x_groq_api_key: str | None = Header(default=None),
    x_github_token: str | None = Header(default=None),
) -> UserCredentials:
    groq_key = _clean(x_groq_api_key)
    github_token = _clean(x_github_token)

    if settings.ALLOW_SERVER_KEY_FALLBACK:
        if not groq_key:
            groq_key = _clean(settings.LLM_API_KEY)

        if not github_token:
            github_token = _clean(settings.GITHUB_TOKEN)

    if not groq_key:
        raise LLMAuthError(
            "Groq API key is missing. Add your key in Settings."
        )

    return UserCredentials(groq_api_key=groq_key, github_token=github_token)