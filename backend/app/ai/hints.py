from __future__ import annotations

import logging
from pathlib import Path
import re

from groq import Groq

from app.core.config import settings
from app.ai.breakdown import _truncate
from app.schemas.ai import HintResponse

logger = logging.getLogger(__name__)

_groq_client : Groq | None = None

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _get_client() -> Groq :
    global _groq_client

    if _groq_client is not None:
        return _groq_client

    api_key = settings.LLM_API_KEY

    if not api_key:
        raise RuntimeError(
            "LLM API Key not configured"
            "Please set LLM API Key"
            )
    _groq_client = Groq(api_key=api_key)

    return _groq_client


def _load_prompt(level : int) -> str :
    if level not in (1,2,3):
        raise ValueError("Hint level must be 1, 2, 3.")

    prompt_path = PROMPTS_DIR / f"hint_{level}.txt"

    if not prompt_path.exists():
        raise FileNotFoundError(f"Hint prompt file not found : {prompt_path}")

    if not prompt_path.is_file():
        raise FileNotFoundError(f"Hint prompt path is not a file : {prompt_path}")

    try :
        return prompt_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise RuntimeError(f"Failed to read hint prompt : {prompt_path}") from exc



def _check_level_allowed(level : int, current_progress : dict) -> bool :
    if level not in (1,2,3):
        raise ValueError("Level must be 1, 2 or 3")

    if level==1:
        return True

    shown_levels = current_progress.get("hint_levels_shown",[])

    if not isinstance(shown_levels,list):
        shown_levels=[]

    if level==2:
        if 1 not in shown_levels:
            raise ValueError("Please request level 1 first")

    if level==3:
        if 1 not in shown_levels:
            raise ValueError("Please request level 1 first")
        
        if 2 not in shown_levels:
            raise ValueError("Please request level 2 first")
    
    return True



def _build_user_message(level:int, issue_context : dict, current_progress : dict) -> str:
    issue = issue_context.get("issue",{})
    repository = issue_context.get("repository",{})
    issue_title = issue.get("title","")
    issue_body = _truncate(str(issue.get("body","")),3000)
    issue_labels = issue.get("labels",[])
    primary_language = repository.get("primary_language","")
    relevant_files = repository.get("relevant_files",[])
    relevant_symbols = repository.get("relevant_symbols",[])
    previous_hints = current_progress.get("previous_hints",{})


    if not isinstance(previous_hints, dict):
        previous_hints={}

    previous_hints_text = []

    for hint_level in ("1","2"):
        hint = previous_hints.get(hint_level)

        if hint:
            previous_hints_text.append(
                f"Level {hint_level}:\n"
                f"{hint}"
            )

    if previous_hints_text:
        previous_hints_text="\n\n".join(previous_hints_text)
    else:
        previous_hints_text="(none)"


    if isinstance(issue_labels, list):
        labels_text = ", ".join(
            str(label)
            for label in issue_labels
        )
    else:
        labels_text=str(issue_labels)


    if isinstance(relevant_files, list):
        files_text ="\n".join(
            str(file)
            for file in relevant_files[:100]
        )
    else:
        files_text=str(relevant_files)


    if isinstance(relevant_symbols, list):
        symbols_text = "\n".join(
            str(symbol)
            for symbol in relevant_symbols[:100]
        )
    else:
        symbols_text=str(relevant_symbols)


    level_instructions = {
        1:(
            "Only tell WHERE to look."
            "No code. No bug explanation."
        ),
        2:(
            "Explain WHAT behavior is wrong."
            "No full patch. No extra code line."
        ),
        3:(
            "Explain How to fix."
            "Code is allowed. Keep the guidance minimal."
        )
    }


    return f"""
    ISSUE :
    - Title : {issue_title}
    - Body : {issue_body}
    - Labels : {issue_labels}

    REPOSITORY CONTEXT:
    - Primary Language : {primary_language}

    Relevant Files:
    {files_text}

    Relevant Symbols:
    {symbols_text}

    PREVIOUS HINTS:
    {previous_hints_text}

    REQUESTED LEVEL:
    {level}

    LEVEL INSTRUCTIONS:
    {level_instructions[level]}

    Return ONLY the hint text.
    No JSON. 
    No markdown wrapper.
""".strip()



def _Validate_hint_output(level:int, hint_text: str) -> tuple[bool,str]:
    if level not in (1,2,3):
        return False, "Invalid hint level."

    if not isinstance(hint_text,str):
        return False, "Hint output must be text."

    hint_text = hint_text.strip()

    if not hint_text:
        return False, "Hint output is empty."

    if level == 3:
        return True,""

    if "```" in hint_text:
        if level==1:
            return False,"Level 1 must not contain code blocks."
        if level==2:
            return False, "Level 2 must not contain multi-line code."

    if level==1:
        forbidden_patterns = [
            (r"\bdef\s+\w+\s*\(", "function definition"),
            (r"\bfunction\s+\w+\s*\(", "function definition"),
            (r"\breturn\s+.+", "return statement"),
            (r"\bline\s+\d+\b", "exact line number"),
            (r"\badd\s+(this|the)\s+line\b", "direct code instruction"),
            (r"\breplace\s+(this|it)\s+with\b", "replacement instruction"),
            (r"\bchange\s+(this|it)\s+to\b", "direct change instruction"),
        ]

        for pattern, reason in forbidden_patterns:
            if re.search(pattern,hint_text,flags=re.IGNORECASE):
                return False, f"Level 1 leaked {reason}."

    if level==2:
        forbidden_patterns = [
            (r"\bwrite\s+`[^`]+`", "inline code instruction"),
            (r"\buse\s+this\s+code\b", "code instruction"),
            (r"\badd\s+this\s+line\b", "direct code instruction"),
            (r"\breplace\s+this\s+with\b", "replacement instruction"),
            (r"\bchange\s+this\s+to\b", "direct implementation instruction"),
        ]

        for pattern, reason in forbidden_patterns:
            if re.search(pattern,hint_text,flags=re.IGNORECASE):
                return False, f"Level 2 leaked {reason}"

    return True,""



def generate_hint(level:int, issue_context:dict, current_progress: dict) -> HintResponse:
    _check_level_allowed(level=level,current_progress=current_progress)

    client = _get_client()

    system_prompt=_load_prompt(level)

    user_message = _build_user_message(
        level=level,
        issue_context=issue_context,
        current_progress=current_progress
    )

    try:
        response = client.chat.completions.create(
            model=settings.LLM_API_MODEL,
            messages=[
                {
                    "role":"system",
                    "content":system_prompt
                },
                {
                    "role":"user",
                    "content":user_message
                },
            ],
            temperature=0.3,
            max_tokens=400,
            stream=False
        )
    except Exception as exc:
        logger.exception(
            "Hint generation failed for level %d",level,
        )
        raise RuntimeError(
            f"Failed to generate level {level} hint."
        ) from exc

    hint_text = response.choices[0].message.content

    if not hint_text:
        raise ValueError(
            f"Groq returned an empty level {level} hint."
        )

    hint_text=hint_text.strip()

    is_valid, validation_error = _Validate_hint_output(level=level, hint_text=hint_text,)

    if not is_valid:
        logger.warning(
            "Invalid level %d hint generated: %s. Retrying.",level,validation_error
        )

        stricter_message = (
        f"{user_message}\n\n"
        "STRICT CORRECTION :\n"
        f"Your previous response was rejected because:"
        f"{validation_error}\n"
        "\n"
        "Generate a new response that strictly follows"
        f"the Level {level} rules.\n"
        "Return ONLY the hint text.\n"
        "Do not explain these instructions."
        )

        try:
            retry_response = client.chat.completions.create(
                model=settings.LLM_API_MODEL,
                messages=[
                    {
                        "role":"system",
                        "content":system_prompt,
                    },
                    {
                        "role":"user",
                        "content": stricter_message,
                    },
                ],
                temperature=0.3,
                max_tokens=400,
                stream=False
            )

        except Exception as exc:
            logger.exception(
                "Hint retry failed for level %d",
                level
            )
            raise RuntimeError(
                f"Failed to generate level {level} hint"
                "after validation retry."
            ) from exc

        hint_text=retry_response.choices[0].message.content

        if not hint_text:
            raise ValueError(
                f"Groq returned an empty level {level} hint "
                "on retry."
            )

        hint_text=hint_text.strip()

        is_valid, validation_error = _Validate_hint_output(
            level=level, hint_text=hint_text,
        )

        if not is_valid:
            raise ValueError(
                f"Generated level {level} hint failed validation"
                f"after retry : {validation_error}"
            )

    hint_text=_truncate(hint_text,800).strip()

    return HintResponse(level=level, hint_text=hint_text)