# backend/app/ai/ranking.py

from __future__ import annotations
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any
from groq import Groq
from app.core.config import settings

logger = logging.getLogger(__name__)

PROMPT_PATH = Path(__file__).parent / "prompts" / "ranking.txt"

REQUIRED_KEYS = [
    "match_score",
    "complexity_level",
    "is_beginner_friendly",
    "required_technologies",
    "matching_skills",
    "missing_or_mismatched_skills",
    "reasoning",
]

DEFAULTS =  {
    "match_score" : 0,
    "complexity_level" : "intermediate",
    "is_beginner_friendly" : False,
    "required_technologies" : [],
    "matching_skills" : [],
    "missing_or_mismatched_skills" : [],
    "reasoning" :"",
}

ALLOWED_COMPLEXITY = {"beginner", "intermediate", "advanced"}

groq_client = Groq(api_key=settings.LLM_API_KEY)


# ───── 1. PUBLIC: PROMPT LOADER ─────
@lru_cache(maxsize=1)
def load_prompt_template() -> str:
    with open(PROMPT_PATH,"r",encoding="utf-8") as file:
        return file.read()


# ───── 2. PUBLIC: SINGLE ISSUE ─────
def rank_issue(issue: dict, user_profile: dict) -> dict:
    prompt=_build_prompt(issue,user_profile)

    raw_response=_call_llm(prompt)

    data=_extract_json(raw_response)

    validate=_validate_response(data)

    validate["issue_id"] = issue["id"]

    return validate


# ───── 3. PUBLIC: MULTIPLE ISSUES ─────
def rank_issues(issues: list[dict], user_profile: dict) -> list[dict]:
    if not issues:
        return []

    results= []

    for issue in issues:
        try:
            result = rank_issue(issue,user_profile)
            results.append(result)
        except Exception as e:
            logger.warning("Failed to rank issue %s",e)
            continue

    sorted_results = sorted(
        results,
        key=lambda r:r["match_score"],
        reverse=True
        )

    return sorted_results


# ───── 4. PRIVATE: BUILD PROMPT ─────
def _build_prompt(issue: dict, user_profile: dict) -> str:
    template = load_prompt_template()
    
    prompt_data= {
            "{user_skills}" : user_profile.get("skills",""),
            "{user_experience_level}" : user_profile.get("experience",""),
            "{issue_title}" : issue.get("title",""),
            "{issue_description}" : issue.get("description",""),
            "{issue_labels}" : issue.get("labels",""),
            "{repository_language}" : issue.get("language","")
        }
    prompt=template
    
    for placeholder, value in prompt_data.items():
        prompt=prompt.replace(placeholder,str(value))
    
    return prompt


# ───── 5. PRIVATE: LLM CALL ─────
def _call_llm(prompt: str) -> str:
    last_error = None

    for attempt in range(2):
        try:
            response = groq_client.chat.completions.create(
                model=settings.LLM_API_MODEL,
                messages=[
                    {
                        "role" : "user",
                        "content" : prompt
                    }
                ],
                temperature=0.2,
                max_tokens=1000,
                stream=False
            )

            raw_text = response.choices[0].message.content
            if not raw_text:
                raise ValueError("Groq return an empty response")

            return raw_text.strip()
        except Exception as e:
            last_error=e
            logger.warning("Grow LLM API CALLED FAILED ATTEMPS (%d/2) : %s",attempt+1,e)
    raise RuntimeError(f"Groq API call failed after retry : {last_error}")


# ───── 6. PRIVATE: EXTRACT JSON ─────
def _extract_json(text: str) -> dict:
    text=text.strip()

    if text.startswith("```json"):
        text=text[len("```json"):]

        if text.endswith("```"):
            text=text[:-3]

        text=text.strip()

    start_idx = text.find("{")
    end_idx= text.rfind("}")

    if start_idx==-1 or end_idx==-1:
        raise ValueError("JSON not found")

    json_str = text[start_idx:end_idx+1]
    try:
        data=json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid json : {e}") from e

    return data


# ───── 7. PRIVATE: VALIDATE ─────
def _validate_response(data: dict) -> dict:
    if not isinstance(data, dict):
        logger.warning("LLM output is not a dict. Using empty dict.")
        data ={}

    for key in REQUIRED_KEYS:
        if key not in data:
            logger.warning("Missing required key: %s, Using default key",key)
            data[key]=DEFAULTS[key]

    try:
        score=float(data["match_score"])
    except (TypeError,ValueError):
        score=0

    score = max(0, min(score,100))

    data["match_score"] = round(score)

    complexity = data["complexity_level"]

    if isinstance(complexity,str):
        complexity=complexity.lower().strip()
    else:
        complexity=""

    if complexity not in ALLOWED_COMPLEXITY:
        complexity = "intermediate"

    data["complexity_level"]=complexity

    beginnerfriendly = data["is_beginner_friendly"]

    if isinstance(beginnerfriendly,bool):
        pass
    elif isinstance(beginnerfriendly,str):
        value= beginnerfriendly.strip().lower()
        if value=="true":
            beginnerfriendly=True
        elif value=="false":
            beginnerfriendly=False
        else:
            beginnerfriendly=False
    else:
        beginnerfriendly=False

    data["is_beginner_friendly"]=beginnerfriendly

    list_fields=[
        "required_technologies",
        "matching_skills",
        "missing_or_mismatched_skills"
    ]

    for field in list_fields:
        value=data[field]

        if isinstance(value,str):
            value=[value]
        elif value is None:
            value=[]
        elif not isinstance(value,list):
            value=[]

        normalized_list=[]

        for item in value:
            if item is not None:
                normalized_list.append(str(item).strip().lower())
        data[field] = normalized_list

    if data["reasoning"] is None:
        data["reasoning"] = ""
    elif not isinstance(data["reasoning"],str):
        data["reasoning"]=str(data["reasoning"])

    return data
