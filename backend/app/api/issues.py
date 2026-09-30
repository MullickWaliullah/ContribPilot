from __future__ import annotations

import logging
import re

from fastapi import APIRouter, HTTPException, Path

from app.schemas.request import (
    RecommendRequest,
    BreakdownRequest,
    RecommendResponse,
    BreakdownWrapper
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
            detail=(
                "GitHub API rate limit exceeded. "
                "Please try again later."
            ),
        )

    if isinstance(exc, github_service.AuthError):
        logger.error("GitHub authentication/configuration error: %s",exc)

        raise HTTPException(
            status_code=500,
            detail="GitHub authentication is not configured correctly.",
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
        detail="Internal server error."
    )



@router.post(
    "/recommend",
    response_model=RecommendResponse,
    )
def recommend_issues(request: RecommendRequest) -> RecommendResponse:
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
def get_issue_breakdown(issue_id: int = Path(..., gt=0, description="GitHub issue number. Must be greater than 0.",), request: BreakdownRequest = ... ) -> BreakdownWrapper:
    repo = _validate_repo(request.repo)

    if not request.skills:
        raise HTTPException(
            status_code=400,
            detail="At least one skill is required."
        )

    try:
        breakdown = ai_service.get_issue_breakdown(
            issue_id=issue_id,
            repo=repo,
            skills=request.skills,
            experience=request.experience,
        )

        return BreakdownWrapper(
            issue_id=issue_id,
            repo=repo,
            breakdown=breakdown,
        )

    except Exception as exc:
        _handle_service_exception(exc)

    raise RuntimeError("Unreachable")