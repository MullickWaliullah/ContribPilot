from __future__ import annotations
from typing import Any

import re
import logging
import time

from app.ai.breakdown import breakdown_issue
from app.ai.ranking import rank_issues
from app.ai.hints import generate_hint

from app.schemas.ai import (RankingResponse, BreakdownResponse, HintResponse)

from app.services import github_service

logger = logging.getLogger(__name__)


_RANKING_CACHE: dict[str,tuple[float,list[RankingResponse]]] ={}
_BREAKDOWN_CACHE: dict[str,tuple[float,BreakdownResponse]] = {}

CACHE_TTL = 60*60


def recommend_issues(skills: list[str], experience: str, repo: str, limit: int = 10,) -> list[RankingResponse]:
    if limit<=0:
        return []

    limit = min(limit,50)

    cache_key = _ranking_cache_key(skills=skills, experience=experience, repo=repo)
    cached = _get_ranking_cache(cache_key)

    if cached is not None:
        return cached[:limit]

    try:
        issues = github_service.search_issues_in_repo(repo=repo, labels=["good-first-issue","bug"], state="open", limit=50,)
    except Exception as exc:
        logger.exception("Failed to fetch issues from GitHub for repo=%s", repo,)
        raise RuntimeError("Failed to fetch issues from GitHub") from exc

    if not issues:
        try:
            issues=github_service.search_issues_in_repo(repo=repo, labels=None, state="open", limit=50)
        except (
        github_service.InvalidRepoError,
        github_service.NotFoundError,
        github_service.RateLimitError,
        github_service.AuthError,
        github_service.ForbiddenError,
        github_service.UpstreamError,
        github_service.UpstreamTimeoutError,
        ):
            raise
        except Exception as exc:
            logger.exception("Failed to fetch fallback issues from GitHub for ")
            raise RuntimeError("Failed to fetch issues from GitHub") from exc

    if not issues:
        _set_ranking_cache(cache_key,[])
        return []

    user_profile = {
        "skills" : skills,
        "experience" : experience
    }

    try:
        ranked_issues = rank_issues(issues=issues, user_profile=user_profile)
    except Exception as exc:
        logger.warning("Failed to rank issues for repo=%s", repo,)
        raise RuntimeError("Failed to rank issues") from exc

    responses : list[RankingResponse]=[]

    for raw_result in ranked_issues:
        try:
            response = _to_ranking_response(raw_result)
            responses.append(response)
        except Exception as exc:
            logger.warning("Skipping invalid ranking result: %s", exc,)


    _set_ranking_cache(cache_key,responses,)

    return responses[:limit]




def get_issue_breakdown(issue_id: int, repo: str, skills: list[str], experience: str,) -> BreakdownResponse:

    cache_key = _breakdown_cache_key(repo=repo, issue_id=issue_id, experience=experience)

    cached = _get_breakdown_cache(cache_key)

    if cached is not None:
        return cached

    try:
        issue = github_service.get_issue(repo=repo, issue_number=issue_id)

    except Exception:
        logger.warning("Failed to fetch issue #%s from repo=%s", issue_id,repo,)
        raise

    try:
        repository_context= _build_repository_context(repo=repo, issue=issue)
    except Exception as exc:
        logger.warning("Failed to build repository context for repo=%s issue=%s",repo,issue_id,)
        raise RuntimeError("Failed to build repository context") from exc

    repository_context["user_skills"] = skills
    repository_context["user_experience"] = experience

    try:
        raw_result = breakdown_issue(issue=issue,repository_context=repository_context,)
    except Exception as exc:
        logger.exception("Failed to generate breakdown for repo=%s issue=%s", repo, issue_id,)

        raise RuntimeError("Failed to generate issue breakdown") from exc

    try:
        response = _to_breakdown_response(raw_result)
    except Exception as exc:
        logger.exception(
            "Invalid breakdown response for repo=%s issue=%s", repo, issue_id,
        )

        raise RuntimeError("Failed to validate issue breakdown") from exc

    _set_breakdown_cache(cache_key,response,)
    return response




def get_hint(level: int, issue_context: dict[str,Any], current_progress: dict[str,Any],) -> HintResponse:

    return generate_hint(level=level, issue_context=issue_context, current_progress=current_progress,)


def _to_ranking_response(raw_dict: dict[str,Any],) -> RankingResponse:

    return RankingResponse(
        issue_id=raw_dict.get("issue_id"),
        match_score=raw_dict.get("match_score",0),
        complexity_level=raw_dict.get("complexity_level","intermediate",),

        is_beginner_friendly=raw_dict.get("is_beginner_friendly", False,),

        required_technologies=raw_dict.get("required_technologies",[],),

        matching_skills=raw_dict.get("matching_skills",[],),

        missing_or_mismatched_skills=raw_dict.get("missing_or_mismatched_skills",[],),

        reasoning=raw_dict.get("reasoning","",),
    )



def _to_breakdown_response(raw_dict: dict[str, Any],) -> BreakdownResponse:
    return BreakdownResponse(
        problem_summary=raw_dict.get("problem_summary","",),

        expected_behavior=raw_dict.get("expected_behavior","",),

        current_behavior=raw_dict.get("current_behavior","",),

        confirmed_facts=raw_dict.get("confirmed_facts",[],),

        files_to_inspect=raw_dict.get("files_to_inspect",[],),

        relevant_symbols=raw_dict.get("relevant_symbols",[],),

        concepts_to_understand=raw_dict.get("concepts_to_understand",[],),

        investigation_steps=raw_dict.get("investigation_steps",[],),

        verification_target=raw_dict.get("verification_target","",),

        context_status=raw_dict.get("context_status","insufficient",),
    )




def _build_hint_issue_context(issue:dict[str, Any], repo: str | None = None, breakdown_result: dict[str, Any] | None = None,) -> dict[str,Any]:
    breakdown_result=breakdown_result or {}

    return {
        "issue": {
            "title":issue.get("title",""),
            "body": issue.get("body",""),
            "labels": issue.get("labels",[]),
        },
        "repository": {
            "name": repo or "",
            "primary_language": issue.get("language","unknown",),
            "relevant_files": breakdown_result.get("files_to_inspect",[],),
            "relevant_symbols": breakdown_result.get("relevant_symbols",[],),
        },
    }


def _build_repository_context(repo: str, issue: dict[str, Any],) -> dict[str, Any]:
    repo_info = github_service.get_repository_info(repo=repo)

    repository_name = repo_info.get("name","",)

    repository_description = repo_info.get("description","",)

    primary_language = repo_info.get("language","unknown",)

    tree_data = github_service.get_repository_tree(repo)

    repository_structure = tree_data.get("files", [],)

    if not isinstance(repository_structure, list):
        repository_structure=[]


    repository_structure=repository_structure[:200]

    relevant_files = _select_relevant_files(issue=issue, files = repository_structure,)

    relevant_source_code: dict[str,str]={}
    existing_tests: dict[str,str]={}

    for file_path in relevant_files:
        try:
            content = github_service.get_file_content(repo=repo, path=file_path,)
        except Exception as exc:
            logger.warning("Skipping file %s because content fetch failed: %s", file_path,exc,)
            continue

        if not isinstance(content,str):
            content=str(content)

        content=content[:4000]

        if _is_test_file(file_path):
            existing_tests[file_path]=content
        else:
            relevant_source_code[file_path]=content

    test_framework = _detect_test_framework(files=repository_structure,)

    return {
        "repository_name": repository_name,
        "repository_description": repository_description,
        "primary_language": primary_language,
        "repository_structure": repository_structure,
        "relevant_files": relevant_files,
        "relevant_source_code": relevant_source_code,
        "existing_tests": existing_tests,
        "test_framework": test_framework,
    }




def _select_relevant_files(issue: dict[str,Any], files: list[str], max_files: int=8,) -> list[str]:
    if not files:
        return []

    issue_text =" ".join(
        [
            str(issue.get("title","")),
            str(issue.get("body","")),
        ]
    )

    issue_text_lower = issue_text.lower()

    selected: list[str]=[]
    selected_set: set[str] = set()

    for file_path in files:
        normalized_path = str(file_path).replace("\\","/")
        if normalized_path.lower() in issue_text_lower:
            if normalized_path not in selected_set:
                selected.append(normalized_path)
                selected_set.add(normalized_path)


    mentioned_paths = re.findall(r"(?:[\w.-]+/)*[\w.-]+\.(?:py|js|jsx|ts|tsx)", issue_text, flags=re.IGNORECASE,)

    mentioned_set = {
        path.replace("\\","/").lower()
        for path in mentioned_paths
    }

    for file_path in files:
        normalized_path = str(file_path).replace("\\","/")

        if normalized_path.lower() in mentioned_set:
            if normalized_path not in selected_set:
                selected.append(normalized_path)
                selected_set.add(normalized_path)


    for file_path in files:
        normalized_path = str(file_path).replace("\\","/")

        if not _is_test_file(normalized_path):
            continue

        if normalized_path not in selected_set:
            selected.append(normalized_path)
            selected_set.add(normalized_path)

        if len(selected)>=max_files:
            return selected[:max_files]

    preferred_source_files: list[str] = []
    other_source_files: list[str]=[]

    for file_path in files:
        normalized_path=str(file_path).replace("\\","/")

        if _is_test_file(normalized_path):
            continue

        lower_path =  normalized_path.lower()

        if(lower_path.startswith("app/") or lower_path.startswith("src/") or lower_path.startswith("lib/")):
            preferred_source_files.append(normalized_path)
        else:
            other_source_files.append(normalized_path)


    for file_path in (preferred_source_files+other_source_files):
        if file_path in selected_set:
            continue

        selected.append(file_path)
        selected_set.add(file_path)

        if len(selected)>=max_files:
            break

    return selected[:max_files]




def _detect_test_framework(files: list[str],) -> str:
    normalized_files = [str(path).replace("\\","/").lower()
                        for path in files]

    for path in normalized_files:
        filename = path.rsplit("/",1)[-1]

        if(filename.startswith("test_") and filename.endswith(".py")):
            return "pytest"

        if (filename.endswith("_test.py")):
            return "pytest"

    for path in normalized_files:
        if(
            path.endswith(".test.js")
            or path.endswith(".test.jsx")
            or path.endswith(".spec.js")
            or path.endswith(".spec.jsx")
        ):
            return "jest"

    for path in normalized_files:
        if(
            path.endswith(".test.ts")
            or path.endswith(".test.tsx")
            or path.endswith(".spec.ts")
            or path.endswith(".spec.tsx")
        ):
            return "jest_or_vitest"

    return "unknown"



def _is_test_file(path: str) -> bool:
    normalized = path.replace("\\","/").lower()

    filename = normalized.rsplit("/",1)[-1]

    if(
        filename.startswith("test_")
        and filename.endswith(".py")
    ):
        return True

    if filename.endswith("_test.py"):
        return True

    if(
        ".test."
        in filename
        or ".spec."
        in filename
    ):
        return True

    parts = normalized.split("/")

    if "tests" in parts:
        return True

    if "__tests__" in parts:
        return True

    return False



def _ranking_cache_key(skills: list[str], experience: str, repo: str,) -> str:
    normalized_skills = sorted(
        str(skill).strip().lower()
        for skill in skills
        if str(skill).strip()
    )

    return (
        f"rank:"
        f"{repo.strip().lower()}:"
        f"{','.join(normalized_skills)}:"
        f"{experience.strip().lower()}"
    )



def _breakdown_cache_key(repo: str, issue_id: int, experience: str,) -> str:
    return (
        f"breakdown:"
        f"{repo.strip().lower()}:"
        f"{issue_id}:"
        f"{experience.strip().lower()}"
    )



def _get_ranking_cache(key: str, )-> list[RankingResponse] | None:
    entry = _RANKING_CACHE.get(key)
    if entry is None:
        return None

    expires_at, value = entry

    if time.monotonic() >= expires_at:
        _RANKING_CACHE.pop(key, None)
        return None

    return value


def _set_ranking_cache(key: str, value: list[RankingResponse]) -> None:
    _RANKING_CACHE[key]=(time.monotonic() + CACHE_TTL, value,)


def _get_breakdown_cache(key:str,) -> BreakdownResponse | None:
    entry = _BREAKDOWN_CACHE.get(key)

    if entry is None:
        return None

    expires_at, value = entry

    if time.monotonic()>=expires_at:
        _BREAKDOWN_CACHE.pop(key,None)
        return None

    return value



def _set_breakdown_cache(key: str, value: BreakdownResponse,) -> None:
    _BREAKDOWN_CACHE[key]= (time.monotonic()+CACHE_TTL, value,)


