from __future__ import annotations
import json
import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.ai.llm_client import (
    LLMError,
    LLMAuthError,
    LLMRateLimitError,
    chat_completion,
)

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "ranking.txt"

REQUIRED_KEYS = [
    "complexity_level",
    "is_beginner_friendly",
    "required_technologies",
    "matching_skills",
    "missing_or_mismatched_skills",
    "skill_score",
    "experience_score",
    "task_score",
    "reasoning",
]

DEFAULTS = {
    "match_score": 0,
    "skill_score": 0,
    "experience_score": 0,
    "task_score": 0,
    "complexity_level": "intermediate",
    "is_beginner_friendly": False,
    "required_technologies": [],
    "matching_skills": [],
    "missing_or_mismatched_skills": [],
    "reasoning": "",
}

ALLOWED_COMPLEXITY = {"beginner", "intermediate", "advanced"}

SKILL_SCORE_MAX = 50
EXPERIENCE_SCORE_MAX = 30
TASK_SCORE_MAX = 20
NON_CONTRIBUTION_SCORE_CAP = 15

BATCH_SIZE = 5
MAX_DESC_CHARS = 500
BASE_OUTPUT_TOKENS = 1500
TOKENS_PER_ISSUE = 350
MAX_TOKENS_CAP = 8000
MAX_RETRIES = 2
MAX_MISSING_PASSES = 2
BATCH_DELAY_SEC = 2.0


@lru_cache(maxsize=1)
def load_prompt_template() -> str:
    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()


def rank_issue(issue: dict, user_profile: dict, api_key: str) -> dict:
    results = rank_issues([issue], user_profile, api_key)
    if not results:
        raise RuntimeError(f"Failed to rank issue {issue.get('id')}")
    return results[0]


def rank_issues(issues: list[dict], user_profile: dict, api_key: str) -> list[dict]:
    if not issues:
        return []

    results_by_id: dict[str, dict] = {}
    pending = list(issues)
    rate_limit_error: LLMRateLimitError | None = None

    for pass_no in range(MAX_MISSING_PASSES + 1):
        if not pending or rate_limit_error is not None:
            break

        batch_size = BATCH_SIZE if pass_no == 0 else max(1, BATCH_SIZE // 2)

        if pass_no > 0:
            logger.info(
                "Retry pass %d for %d missing issues (batch_size=%d)",
                pass_no, len(pending), batch_size,
            )

        chunks = list(_chunk(pending, batch_size))
        for idx, chunk in enumerate(chunks):
            try:
                for res in _rank_batch(chunk, user_profile, api_key):
                    results_by_id[_norm_id(res["issue_id"])] = res
            except LLMAuthError:
                raise
            except LLMRateLimitError as e:
                logger.warning("Rate limited while ranking: %s", e)
                rate_limit_error = e
                break
            except Exception as e:
                logger.warning(
                    "Batch failed for issues %s: %s",
                    [i.get("id") for i in chunk], e,
                )

            if idx < len(chunks) - 1:
                time.sleep(BATCH_DELAY_SEC)

        pending = [i for i in pending if _norm_id(i["id"]) not in results_by_id]

        if pending and pass_no < MAX_MISSING_PASSES and rate_limit_error is None:
            time.sleep(BATCH_DELAY_SEC)

    if rate_limit_error is not None and not results_by_id:
        raise rate_limit_error

    for issue in pending:
        logger.error("Giving up on issue %s, using fallback result", issue.get("id"))
        results_by_id[_norm_id(issue["id"])] = _fallback_result(issue)

    return sorted(results_by_id.values(), key=lambda r: r["match_score"], reverse=True)


def _rank_batch(issues: list[dict], user_profile: dict, api_key: str) -> list[dict]:
    prompt = _build_prompt(issues, user_profile)
    raw_response, truncated = _call_llm(prompt, api_key, num_issues=len(issues))

    items = _parse_results(raw_response, truncated)

    by_id: dict[str, dict] = {}
    for item in items:
        if isinstance(item, dict) and "issue_id" in item:
            by_id[_norm_id(item["issue_id"])] = item

    results = []
    for issue in issues:
        item = by_id.get(_norm_id(issue["id"]))
        if item is None:
            logger.warning("LLM did not return result for issue %s", issue["id"])
            continue

        validated = _validate_item(item)
        validated["issue_id"] = issue["id"]
        results.append(validated)

    logger.info("Batch: got %d/%d results", len(results), len(issues))
    return results


def _chunk(items: list, size: int):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _norm_id(value: Any) -> str:
    return str(value).strip().lstrip("#").strip()


def _fallback_result(issue: dict) -> dict:
    result = {
        k: (list(v) if isinstance(v, list) else v) for k, v in DEFAULTS.items()
    }
    result["reasoning"] = "AI ranking unavailable for this issue."
    result["issue_id"] = issue["id"]
    result["ranking_failed"] = True
    return result


def _build_prompt(issues: list[dict], user_profile: dict) -> str:
    template = load_prompt_template()

    issues_payload = [
        {
            "id": str(issue["id"]),
            "title": issue.get("title", ""),
            "description": str(issue.get("description", "") or "")[:MAX_DESC_CHARS],
            "labels": issue.get("labels", ""),
            "repository_language": issue.get("language", ""),
        }
        for issue in issues
    ]

    prompt_data = {
        "{user_skills}": user_profile.get("skills", ""),
        "{user_experience_level}": user_profile.get("experience", ""),
        "{issues_json}": json.dumps(issues_payload, ensure_ascii=False, indent=2),
    }

    prompt = template
    for placeholder, value in prompt_data.items():
        prompt = prompt.replace(placeholder, str(value))

    return prompt


def _call_llm(prompt: str, api_key: str, num_issues: int = 1) -> tuple[str, bool]:
    last_error = None
    max_tokens = min(BASE_OUTPUT_TOKENS + num_issues * TOKENS_PER_ISSUE, MAX_TOKENS_CAP)

    for attempt in range(MAX_RETRIES):
        try:
            response = chat_completion(
                api_key=api_key,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=max_tokens,
                stream=False,
                response_format={"type": "json_object"},
            )

            choice = response.choices[0]
            raw_text = choice.message.content
            if not raw_text:
                raise ValueError("Groq returned an empty response")

            truncated = choice.finish_reason == "length"
            if truncated:
                logger.warning(
                    "LLM output truncated (finish_reason=length, max_tokens=%d, issues=%d)",
                    max_tokens, num_issues,
                )

            return raw_text.strip(), truncated

        except LLMError:
            raise
        except Exception as e:
            last_error = e
            logger.warning(
                "Groq LLM API call failed attempt (%d/%d): %s",
                attempt + 1, MAX_RETRIES, e,
            )
            time.sleep(BATCH_DELAY_SEC)

    raise RuntimeError(f"Groq API call failed after retry: {last_error}")


def _parse_results(raw: str, truncated: bool) -> list[dict]:
    try:
        data = _extract_json(raw)
        items = data.get("results")
        if isinstance(items, list):
            return items
        raise ValueError("LLM response missing 'results' list")
    except ValueError as e:
        logger.warning("Full JSON parse failed (%s). Trying to salvage partial results.", e)
        salvaged = _salvage_partial_results(raw)
        if not salvaged:
            raise
        logger.info("Salvaged %d complete results from broken JSON", len(salvaged))
        return salvaged


def _extract_json(text: str) -> dict:
    text = text.strip()

    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
        text = text.strip()

    start_idx = text.find("{")
    end_idx = text.rfind("}")

    if start_idx == -1 or end_idx == -1:
        raise ValueError("JSON not found")

    try:
        data = json.loads(text[start_idx:end_idx + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid json: {e}") from e

    if not isinstance(data, dict):
        raise ValueError("Top-level JSON is not an object")

    return data


def _salvage_partial_results(text: str) -> list[dict]:
    key_idx = text.find('"results"')
    if key_idx == -1:
        return []

    arr_start = text.find("[", key_idx)
    if arr_start == -1:
        return []

    decoder = json.JSONDecoder()
    pos = arr_start + 1
    items: list[dict] = []

    while pos < len(text):
        while pos < len(text) and text[pos] in " \t\r\n,":
            pos += 1
        if pos >= len(text) or text[pos] != "{":
            break
        try:
            obj, end = decoder.raw_decode(text, pos)
        except json.JSONDecodeError:
            break
        if isinstance(obj, dict):
            items.append(obj)
        pos = end

    return items


def _clamp_score(value: Any, low: int, high: int) -> int:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 0
    return round(max(low, min(number, high)))


def _validate_item(data: dict) -> dict:
    if not isinstance(data, dict):
        logger.warning("LLM item is not a dict. Using empty dict.")
        data = {}

    for key in REQUIRED_KEYS:
        if key not in data:
            logger.warning("Missing required key: %s, using default", key)
            default = DEFAULTS[key]
            data[key] = list(default) if isinstance(default, list) else default

    skill_score = _clamp_score(data["skill_score"], 0, SKILL_SCORE_MAX)
    experience_score = _clamp_score(data["experience_score"], 0, EXPERIENCE_SCORE_MAX)
    task_score = _clamp_score(data["task_score"], 0, TASK_SCORE_MAX)

    total = skill_score + experience_score + task_score

    if task_score == 0:
        total = min(total, NON_CONTRIBUTION_SCORE_CAP)

    data["skill_score"] = skill_score
    data["experience_score"] = experience_score
    data["task_score"] = task_score
    data["match_score"] = total

    complexity = data["complexity_level"]
    complexity = complexity.lower().strip() if isinstance(complexity, str) else ""
    if complexity not in ALLOWED_COMPLEXITY:
        complexity = "intermediate"
    data["complexity_level"] = complexity

    bf = data["is_beginner_friendly"]
    if isinstance(bf, str):
        bf = bf.strip().lower() == "true"
    elif not isinstance(bf, bool):
        bf = False
    data["is_beginner_friendly"] = bf

    for field in ("required_technologies", "matching_skills", "missing_or_mismatched_skills"):
        value = data[field]
        if isinstance(value, str):
            value = [value]
        elif not isinstance(value, list):
            value = []
        data[field] = [str(item).strip().lower() for item in value if item is not None]

    if data["reasoning"] is None:
        data["reasoning"] = ""
    elif not isinstance(data["reasoning"], str):
        data["reasoning"] = str(data["reasoning"])

    return data