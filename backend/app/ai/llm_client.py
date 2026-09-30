from __future__ import annotations

import logging
from typing import Any

from groq import (
    Groq,
    AuthenticationError,
    BadRequestError,
    PermissionDeniedError,
    RateLimitError,
)

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    pass


class LLMAuthError(LLMError):
    pass


class LLMRateLimitError(LLMError):
    pass


def get_groq_client(api_key: str | None) -> Groq:
    if not api_key or not api_key.strip():
        raise LLMAuthError(
            "Groq API key is missing. Add your key in Settings."
        )

    return Groq(api_key=api_key.strip())


def _create_with_json_fallback(client: Groq, kwargs: dict[str, Any]):
    try:
        return client.chat.completions.create(**kwargs)
    except BadRequestError as exc:
        if "response_format" in kwargs and "json_validate_failed" in str(exc):
            logger.warning(
                "Groq JSON mode validation failed, retrying without response_format"
            )
            retry_kwargs = {
                key: value for key, value in kwargs.items() if key != "response_format"
            }
            return client.chat.completions.create(**retry_kwargs)
        raise


def chat_completion(api_key: str | None, **kwargs: Any):
    client = get_groq_client(api_key)

    kwargs.setdefault("model", settings.LLM_API_MODEL)

    try:
        return _create_with_json_fallback(client, kwargs)
    except (AuthenticationError, PermissionDeniedError) as exc:
        raise LLMAuthError(
            "Invalid or unauthorized Groq API key. Please check your key in Settings."
        ) from exc
    except RateLimitError as exc:
        raise LLMRateLimitError(
            "Groq rate limit reached for this API key. Please wait a moment and try again."
        ) from exc