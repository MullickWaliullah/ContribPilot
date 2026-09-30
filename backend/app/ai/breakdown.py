from __future__ import annotations
import json
import logging
import time
from pathlib import Path

from app.ai.llm_client import LLMError, chat_completion

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "breakdown.txt"

INITIAL_MAX_TOKENS = 4000
RETRY_MAX_TOKENS = 6000
MAX_ATTEMPTS = 3
RETRY_DELAY_SEC = 2.0

MAX_ISSUE_BODY_CHARS = 3000
MAX_STRUCTURE_ITEMS = 200
MAX_RELEVANT_FILES = 30
MAX_SOURCE_FILES = 10
MAX_TEST_FILES = 5
MAX_FILE_CHARS = 3000


def _load_prompt() -> str:
    if not PROMPT_PATH.exists():
        raise FileNotFoundError(f"Breakdown prompt file not found : {PROMPT_PATH}")

    if not PROMPT_PATH.is_file():
        raise FileNotFoundError(f"Breakdown prompt path is not a file : {PROMPT_PATH}")

    with open(PROMPT_PATH, "r", encoding="utf-8") as file:
        return file.read()


def _truncate(text: str, limit: int) -> str:
    if limit < 0:
        raise ValueError("Truncate limit cannot be negative")

    if len(text) <= limit:
        return text

    return text[:limit] + "...[truncate]"


def _build_user_message(issue: dict, repository_context: dict) -> str:
    repository_name = repository_context.get("repository_name", "")
    repository_description = repository_context.get("repository_description", "")
    primary_language = repository_context.get("primary_language", "")
    repository_structure = repository_context.get("repository_structure", [])
    relevant_files = repository_context.get("relevant_files", [])
    relevant_source_code = repository_context.get("relevant_source_code", {})
    existing_tests = repository_context.get("existing_tests", {})
    issue_title = issue.get("title", "")
    issue_body = _truncate(str(issue.get("body", "") or ""), MAX_ISSUE_BODY_CHARS)
    issue_labels = issue.get("labels", [])

    if isinstance(issue_labels, list):
        issue_labels_text = ",".join(str(label) for label in issue_labels)
    else:
        issue_labels_text = str(issue_labels)

    if isinstance(repository_structure, list):
        structure_text = "\n".join(
            str(path) for path in repository_structure[:MAX_STRUCTURE_ITEMS]
        )
    else:
        structure_text = str(repository_structure)

    if isinstance(relevant_files, list):
        relevant_files_text = "\n".join(
            str(path) for path in relevant_files[:MAX_RELEVANT_FILES]
        )
    else:
        relevant_files_text = str(relevant_files)

    source_sections = []

    if isinstance(relevant_source_code, dict):
        for file_path, content in list(relevant_source_code.items())[:MAX_SOURCE_FILES]:
            source_sections.append(
                f"--- FILE : {file_path} ---\n"
                f"{_truncate(str(content), MAX_FILE_CHARS)}\n"
                f"--- END FILE ---"
            )
    elif relevant_source_code:
        source_sections.append(_truncate(str(relevant_source_code), MAX_FILE_CHARS))

    source_code_text = "\n\n".join(source_sections)

    test_sections = []

    if isinstance(existing_tests, dict):
        for file_path, content in list(existing_tests.items())[:MAX_TEST_FILES]:
            test_sections.append(
                f"--- TEST FILE : {file_path} ---\n"
                f"{_truncate(str(content), MAX_FILE_CHARS)}\n"
                f"--- END FILE ---"
            )
    elif isinstance(existing_tests, list):
        test_sections.append(
            "\n".join(str(test) for test in existing_tests[:MAX_TEST_FILES])
        )
    elif existing_tests:
        test_sections.append(_truncate(str(existing_tests), MAX_FILE_CHARS))

    existing_tests_text = "\n\n".join(test_sections)

    return f"""
    Issue Information :
    - Title : {issue_title}
    - Body : {issue_body}
    - Labels : {issue_labels_text}

    Repository Context :
    - Repository Name : {repository_name}
    - Description : {repository_description}
    - Primary Language : {primary_language}
    - Directory Structure : {structure_text}

    - Relevant Files : {relevant_files_text}

    - Relevant Source Code: {source_code_text}

    - Existing Tests : {existing_tests_text}
""".strip()


def _call_llm(
    api_key: str,
    system_prompt: str,
    user_message: str,
    max_tokens: int,
) -> tuple[str, bool]:
    response = chat_completion(
        api_key=api_key,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
        max_tokens=max_tokens,
        stream=False,
        response_format={"type": "json_object"},
    )

    choice = response.choices[0]
    raw_text = (choice.message.content or "").strip()

    if not raw_text:
        raise ValueError("Groq returned an empty response")

    truncated = choice.finish_reason == "length"

    if truncated:
        logger.warning(
            "Breakdown output truncated (finish_reason=length, max_tokens=%d)",
            max_tokens,
        )

    return raw_text, truncated


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
        raise ValueError("JSON not found in Groq response")

    try:
        data = json.loads(text[start_idx:end_idx + 1])
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid json : {exc}") from exc

    if not isinstance(data, dict):
        raise ValueError("Groq breakdown must be json object")

    return data


def _validate_against_context(result: dict, repository_context: dict) -> dict:
    tree = repository_context.get("repository_structure", [])
    relevant_files = repository_context.get("relevant_files", [])
    source_code = repository_context.get("relevant_source_code", {})

    known_files: set[str] = set()

    if isinstance(tree, list):
        known_files.update(str(path) for path in tree)

    if isinstance(relevant_files, list):
        known_files.update(str(path) for path in relevant_files)

    if isinstance(source_code, dict):
        known_files.update(str(path) for path in source_code.keys())

    file_content: dict[str, str] = {}

    if isinstance(source_code, dict):
        for file_path, content in source_code.items():
            file_content[str(file_path)] = str(content)

    files_to_inspect = result.get("files_to_inspect", [])

    if not isinstance(files_to_inspect, list):
        files_to_inspect = []

    valid_files = []

    for file_path in files_to_inspect:
        file_path = str(file_path).strip()

        if not file_path:
            continue

        if file_path in known_files:
            valid_files.append(file_path)

    result["files_to_inspect"] = valid_files

    relevant_symbols = result.get("relevant_symbols", [])

    if not isinstance(relevant_symbols, list):
        relevant_symbols = []

    valid_symbol = []

    for symbol in relevant_symbols:
        symbol = str(symbol).strip()

        if not symbol:
            continue

        symbol_found = False

        if "." in symbol:
            parts = symbol.split(".", 1)

            if len(parts) == 2:
                class_name, method_name = parts

                for content in file_content.values():
                    if class_name in content and method_name in content:
                        symbol_found = True
                        break
        else:
            for content in file_content.values():
                if symbol in content:
                    symbol_found = True
                    break

        if symbol_found:
            valid_symbol.append(symbol)

    result["relevant_symbols"] = valid_symbol

    return result


def breakdown_issue(issue: dict, repository_context: dict, api_key: str) -> dict:
    system_prompt = _load_prompt()

    user_message = _build_user_message(issue, repository_context)

    last_error: Exception | None = None

    for attempt in range(MAX_ATTEMPTS):
        max_tokens = INITIAL_MAX_TOKENS if attempt == 0 else RETRY_MAX_TOKENS

        try:
            raw_response, truncated = _call_llm(
                api_key, system_prompt, user_message, max_tokens
            )

            if truncated:
                raise ValueError(
                    f"Groq output was truncated at {max_tokens} tokens"
                )

            data = _extract_json(raw_response)

            return _validate_against_context(data, repository_context)

        except LLMError:
            raise

        except Exception as exc:
            last_error = exc

            logger.warning(
                "Breakdown attempt (%d/%d) failed: %s",
                attempt + 1,
                MAX_ATTEMPTS,
                exc,
            )

            if attempt < MAX_ATTEMPTS - 1:
                time.sleep(RETRY_DELAY_SEC)

    raise RuntimeError(f"Breakdown failed after {MAX_ATTEMPTS} attempts : {last_error}")