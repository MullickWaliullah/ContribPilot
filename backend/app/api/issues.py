from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Path

from app.ai.llm_client import LLMError
from app.core.credentials import UserCredentials, get_credentials
from app.schemas.request import (
    RecommendRequest,
    BreakdownRequest,
    RecommendResponse,
    BreakdownWrapper,
)

from app.services import ai_service, github_service

logger = logging.getLogger(__name__)

router = APIRouter()


REPO_PATTERN = re.compile(r"^[^/\s]+/[^/\s]+$")


def _validate_repo(repo: str) -> str:
    repo = repo.strip()

    if not REPO_PATTERN.fullmatch(repo):
        raise HTTPException(
            status_code=400,
            detail="Invalid repository format. Expected 'owner/repo'.",
        )
    return repo


def _handle_service_exception(exc: Exception) -> None:
    if isinstance(exc, LLMError):
        raise exc

    if isinstance(exc, github_service.InvalidRepoError):
        raise HTTPException(
            status_code=400,
            detail=str(exc) or "Invalid GitHub repository.",
        )

    if isinstance(exc, github_service.NotFoundError):
        raise HTTPException(
            status_code=404,
            detail=str(exc) or "Repository or issue not found.",
        )

    if isinstance(exc, github_service.RateLimitError):
        raise HTTPException(
            status_code=429,
            detail=str(exc) or "GitHub API rate limit exceeded. Please try again later.",
        )

    if isinstance(exc, github_service.AuthError):
        logger.warning("GitHub token rejected: %s", exc)

        raise HTTPException(
            status_code=401,
            detail="Invalid GitHub token. Please check your token in Settings.",
        )

    if isinstance(exc, ValueError):
        raise HTTPException(
            status_code=400,
            detail=str(exc) or "Invalid request.",
        )

    if isinstance(exc, RuntimeError):
        raise HTTPException(
            status_code=502,
            detail=str(exc) or "Upstream service failed.",
        )

    logger.exception("Unexpected API error: %s", exc)

    raise HTTPException(
        status_code=500,
        detail="Internal server error.",
    )


@router.post(
    "/recommend",
    response_model=RecommendResponse,
)
def recommend_issues(
    request: RecommendRequest,
    credentials: UserCredentials = Depends(get_credentials),
) -> RecommendResponse:
    repo = _validate_repo(request.repo)

    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="At least one skill is required.",
        )

    try:
        issues = ai_service.recommend_issues(
            skills=request.skills,
            experience=request.experience,
            repo=repo,
            credentials=credentials,
            limit=request.limit,
        )

        return RecommendResponse(
            issues=issues,
            total=len(issues),
            repo=repo,
        )

    except Exception as exc:
        _handle_service_exception(exc=exc)

    raise RuntimeError("Unreachable")


@router.post(
    "/{issue_id}/breakdown",
    response_model=BreakdownWrapper,
)
def get_issue_breakdown(
    issue_id: int = Path(..., gt=0, description="GitHub issue number. Must be greater than 0."),
    request: BreakdownRequest = ...,
    credentials: UserCredentials = Depends(get_credentials),
) -> BreakdownWrapper:
    repo = _validate_repo(request.repo)

    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="At least one skill is required.",
        )

    try:
        breakdown = ai_service.get_issue_breakdown(
            issue_id=issue_id,
            repo=repo,
            skills=request.skills,
            experience=request.experience,
            credentials=credentials,
        )

        return BreakdownWrapper(
            issue_id=issue_id,
            repo=repo,
            breakdown=breakdown,
        )

    except Exception as exc:
        _handle_service_exception(exc)

    raise RuntimeError("Unreachable")