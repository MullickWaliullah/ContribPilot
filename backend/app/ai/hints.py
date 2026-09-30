from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from app.ai.breakdown import _truncate
from app.ai.llm_client import LLMError, chat_completion
from app.schemas.ai import HintResponse

logger = logging.getLogger(__name__)

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load_prompt(level: int) -> str:
    if level not in (1, 2, 3):
        raise ValueError("Hint level must be 1, 2 or 3.")

    prompt_path = PROMPTS_DIR / f"hint_{level}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(
            f"Hint prompt file not found: {prompt_path}"
        )

    if not prompt_path.is_file():
        raise FileNotFoundError(
            f"Hint prompt path is not a file: {prompt_path}"
        )

    try:
        prompt = prompt_path.read_text(
            encoding="utf-8"
        ).strip()
    except OSError as exc:
        raise RuntimeError(
            f"Failed to read hint prompt: {prompt_path}"
        ) from exc

    if not prompt:
        raise ValueError(
            f"Hint prompt file is empty: {prompt_path}"
        )

    return prompt


def _check_level_allowed(
    level: int,
    current_progress: dict[str, Any],
) -> bool:
    if level not in (1, 2, 3):
        raise ValueError(
            "Hint level must be 1, 2 or 3."
        )

    return True


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, tuple):
        return list(value)

    if isinstance(value, str):
        value = value.strip()

        if not value:
            return []

        return [value]

    return [value]


def _build_user_message(
    level: int,
    issue_context: dict[str, Any],
    current_progress: dict[str, Any],
) -> str:

    if not isinstance(issue_context, dict):
        issue_context = {}

    if not isinstance(current_progress, dict):
        current_progress = {}

    issue = issue_context.get("issue", {})
    repository = issue_context.get("repository", {})

    if not isinstance(issue, dict):
        issue = {}

    if not isinstance(repository, dict):
        repository = {}

    issue_title = str(
        issue.get("title")
        or issue_context.get("title")
        or ""
    ).strip()

    issue_body = str(
        issue.get("body")
        or issue_context.get("body")
        or ""
    ).strip()

    issue_body = _truncate(
        issue_body,
        3000,
    )

    issue_labels = (
        issue.get("labels")
        or issue_context.get("labels")
        or []
    )

    primary_language = str(
        repository.get("primary_language")
        or repository.get("language")
        or issue_context.get("primary_language")
        or issue_context.get("language")
        or ""
    ).strip()

    repository_name = str(
        repository.get("name")
        or repository.get("full_name")
        or issue_context.get("repo")
        or issue_context.get("repository")
        or ""
    ).strip()

    relevant_files = (
        repository.get("relevant_files")
        or issue_context.get("files_to_inspect")
        or []
    )

    relevant_symbols = (
        repository.get("relevant_symbols")
        or issue_context.get("relevant_symbols")
        or []
    )

    concepts_to_understand = _as_list(
        issue_context.get("concepts_to_understand")
        or issue_context.get("concepts")
    )

    confirmed_facts = _as_list(
        issue_context.get("confirmed_facts")
    )

    investigation_steps = _as_list(
        issue_context.get("investigation_steps")
    )

    verification_target = str(
        issue_context.get("verification_target")
        or ""
    ).strip()

    focus_summary = str(
        issue_context.get("focus_summary")
        or issue_context.get("problem_summary")
        or ""
    ).strip()

    current_behavior = str(
        issue_context.get("current_behavior")
        or ""
    ).strip()

    expected_behavior = str(
        issue_context.get("expected_behavior")
        or ""
    ).strip()

    if not issue_body and focus_summary:
        issue_body = _truncate(
            focus_summary,
            3000,
        )

    previous_hints = current_progress.get(
        "previous_hints",
        {},
    )

    if not isinstance(previous_hints, dict):
        previous_hints = {}

    previous_hint_parts = []

    for level_number, hint in previous_hints.items():
        if hint is None:
            continue

        hint_value = str(hint).strip()

        if not hint_value:
            continue

        previous_hint_parts.append(
            f"Level {level_number}: {hint_value}"
        )

    previous_hint_text = "\n".join(
        previous_hint_parts
    )

    if level == 1:
        level_instruction = """
Give the contributor a useful starting point.

Explain where they should look in the repository
and which files, classes, functions, modules, or
code areas are likely relevant.

Keep it focused on helping them start investigating.
"""

    elif level == 2:
        level_instruction = """
Explain the relevant logic behind the issue.

Describe what behavior needs to be understood,
what part of the existing implementation matters,
and what should be investigated.

Give enough detail to help the contributor move
towards the solution.
"""

    else:
        level_instruction = """
Give a concrete solution direction.

Explain how the contributor can approach fixing
the issue.

You may provide code examples or implementation
details if useful.

Keep the solution directly related to the issue.
"""

    return f"""
Generate a level {level} hint for an open-source
contribution.

Repository:
{repository_name or "Not provided"}

Issue title:
{issue_title or "Not provided"}

Issue description:
{issue_body or "Not provided"}

Focus summary:
{focus_summary or "Not provided"}

Current behavior:
{current_behavior or "Not provided"}

Expected behavior:
{expected_behavior or "Not provided"}

Issue labels:
{issue_labels}

Primary language:
{primary_language or "Not provided"}

Relevant files:
{relevant_files}

Relevant symbols:
{relevant_symbols}

Concepts to understand:
{concepts_to_understand}

Confirmed facts:
{confirmed_facts}

Investigation steps:
{investigation_steps}

Verification target:
{verification_target or "Not provided"}

Previously shown hints:
{previous_hint_text or "None"}

The user can request any hint level directly.
Do not assume previous hint levels were completed.

Instructions for this hint level:
{level_instruction}

Return only the hint content.
Do not return JSON.
Do not add unnecessary metadata.
""".strip()


def _clean_hint_text(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, str):
        return value.strip()

    return str(value).strip()


def _extract_response_text(response: Any) -> str:
    if response is None:
        return ""

    choices = getattr(
        response,
        "choices",
        None,
    )

    if not choices:
        return ""

    first_choice = choices[0]

    message = getattr(
        first_choice,
        "message",
        None,
    )

    if message is not None:

        content = getattr(
            message,
            "content",
            None,
        )

        if isinstance(content, str):
            return _clean_hint_text(content)

        if isinstance(content, list):

            text_parts = []

            for item in content:

                if isinstance(item, str):
                    text_parts.append(item)
                    continue

                if isinstance(item, dict):

                    item_text = item.get("text")

                    if item_text:
                        text_parts.append(
                            str(item_text)
                        )

                    continue

                item_text = getattr(
                    item,
                    "text",
                    None,
                )

                if item_text:
                    text_parts.append(
                        str(item_text)
                    )

            return _clean_hint_text(
                "\n".join(text_parts)
            )

    text = getattr(
        first_choice,
        "text",
        None,
    )

    if text:
        return _clean_hint_text(text)

    return ""


def _request_hint(
    *,
    api_key: str,
    system_prompt: str,
    user_message: str,
    level: int,
    temperature: float = 0.3,
) -> str:

    try:

        response = chat_completion(
            api_key=api_key,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_message,
                },
            ],
            temperature=temperature,
            max_tokens=500,
            stream=False,
        )

    except LLMError:
        raise

    except Exception as exc:

        logger.exception(
            "Hint generation failed for level %d",
            level,
        )

        raise RuntimeError(
            f"Failed to generate level {level} hint."
        ) from exc

    hint_text = _extract_response_text(
        response
    )

    if not hint_text:

        logger.error(
            "Groq returned an empty response for "
            "level %d. Response=%r",
            level,
            response,
        )

        raise ValueError(
            f"Groq returned an empty level {level} hint."
        )

    return hint_text


def generate_hint(
    *,
    level: int,
    issue_context: dict,
    current_progress: dict,
    api_key: str,
) -> HintResponse:

    _check_level_allowed(
        level=level,
        current_progress=current_progress,
    )

    system_prompt = _load_prompt(level)

    user_message = _build_user_message(
        level=level,
        issue_context=issue_context,
        current_progress=current_progress,
    )

    hint_text = _request_hint(
        api_key=api_key,
        system_prompt=system_prompt,
        user_message=user_message,
        level=level,
        temperature=0.3,
    )

    hint_text = hint_text.strip()

    if not hint_text:
        raise ValueError(
            f"Generated level {level} hint is empty."
        )

    return HintResponse(
        level=level,
        hint_text=hint_text,
    )