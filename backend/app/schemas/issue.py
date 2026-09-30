"""
Schemas for user skills, normalized GitHub issues, AI recommendations
and issue breakdowns.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# Enums / helpers
# --------------------------------------------------------------------------- #

class ExperienceLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


_DIFFICULTY_ALIASES: dict[str, str] = {
    "easy": "easy",
    "beginner": "easy",
    "trivial": "easy",
    "low": "easy",
    "medium": "medium",
    "intermediate": "medium",
    "moderate": "medium",
    "hard": "hard",
    "advanced": "hard",
    "difficult": "hard",
    "complex": "hard",
}


def _normalize_difficulty(value: Any) -> str | None:
    """Map free-form LLM/GitHub difficulty strings onto our enum."""
    if value is None:
        return None
    token = str(value).strip().lower()
    return _DIFFICULTY_ALIASES.get(token, Difficulty.MEDIUM.value)


def _normalize_str_list(value: Any) -> list[str]:
    """Accept str | list[str] | None -> clean, lowercased, de-duplicated list."""
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    seen: set[str] = set()
    out: list[str] = []
    for item in value:
        token = str(item).strip().lower()
        if token and token not in seen:
            seen.add(token)
            out.append(token)
    return out


# --------------------------------------------------------------------------- #
# User input
# --------------------------------------------------------------------------- #

class UserSkills(BaseModel):
    """Body of `POST /api/issues/recommend`."""

    model_config = ConfigDict(extra="ignore")

    skills: list[str] = Field(
        default_factory=list,
        description="Free-form skill tags, e.g. ['python', 'pytest'].",
        examples=[["python", "pytest"]],
    )
    experience: ExperienceLevel = Field(
        default=ExperienceLevel.BEGINNER,
        description="Self-reported experience level.",
    )
    languages: list[str] = Field(
        default_factory=list,
        description="Preferred programming languages.",
    )
    interests: list[str] = Field(
        default_factory=list,
        description="Optional topic interests, e.g. ['cli', 'docs'].",
    )

    @field_validator("skills", "languages", "interests", mode="before")
    @classmethod
    def _clean_lists(cls, value: Any) -> list[str]:
        return _normalize_str_list(value)


# --------------------------------------------------------------------------- #
# GitHub data (normalized — never a raw GitHub payload)
# --------------------------------------------------------------------------- #

class Repository(BaseModel):
    """Normalized repository metadata."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    full_name: str = Field(description="'owner/repo'.")
    name: str | None = None
    owner: str | None = None
    url: str = Field(alias="html_url", description="Web URL of the repository.")
    description: str | None = None
    language: str | None = None
    stars: int = Field(default=0, ge=0)
    forks: int = Field(default=0, ge=0)
    open_issues: int = Field(default=0, ge=0)
    default_branch: str = "main"
    topics: list[str] = Field(default_factory=list)


class Issue(BaseModel):
    """Normalized GitHub issue."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    id: int
    number: int
    title: str
    body: str | None = None
    url: str = Field(alias="html_url", description="Web URL of the issue.")
    repository: str = Field(description="'owner/repo' the issue belongs to.")
    repository_url: str | None = None
    language: str | None = None
    labels: list[str] = Field(default_factory=list)
    state: str = Field(default="open")
    comments: int = Field(default=0, ge=0)
    difficulty: Difficulty | None = None
    is_good_first_issue: bool = False
    is_hacktoberfest: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    @field_validator("labels", mode="before")
    @classmethod
    def _clean_labels(cls, value: Any) -> list[str]:
        if value is None:
            return []
        out: list[str] = []
        for item in value:
            if isinstance(item, dict):
                item = item.get("name", "")
            token = str(item).strip()
            if token:
                out.append(token)
        return out

    @field_validator("difficulty", mode="before")
    @classmethod
    def _clean_difficulty(cls, value: Any) -> str | None:
        return _normalize_difficulty(value)


class IssueDetailResponse(BaseModel):
    """Body of `GET /api/issues/{issue_id}`."""

    model_config = ConfigDict(extra="ignore")

    issue: Issue
    repository: Repository | None = None


# --------------------------------------------------------------------------- #
# AI output
# --------------------------------------------------------------------------- #

class RecommendedIssue(BaseModel):
    """A single ranked issue returned by the AI module."""

    model_config = ConfigDict(extra="ignore")

    id: int = Field(description="GitHub issue id.")
    title: str
    repository: str = Field(description="'owner/repo'.")
    url: str
    language: str | None = None
    labels: list[str] = Field(default_factory=list)
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)
    match_score: float = Field(
        ge=0.0,
        le=100.0,
        description="0–100 match score. Values in (0, 1] are scaled to 0–100.",
    )
    reason: str = Field(description="Short human-readable justification.")

    # Optional context the frontend may display.
    number: int | None = None
    comments: int | None = Field(default=None, ge=0)
    body_preview: str | None = None

    @field_validator("match_score", mode="before")
    @classmethod
    def _normalize_match_score(cls, value: Any) -> float:
        try:
            score = float(value)
        except (TypeError, ValueError):
            return 0.0
        if 0.0 < score <= 1.0:  # LLM returned a probability
            score *= 100.0
        return max(0.0, min(100.0, score))

    @field_validator("difficulty", mode="before")
    @classmethod
    def _clean_difficulty(cls, value: Any) -> str:
        return _normalize_difficulty(value) or Difficulty.MEDIUM.value

    @field_validator("labels", mode="before")
    @classmethod
    def _clean_labels(cls, value: Any) -> list[str]:
        return _normalize_str_list(value)


class BreakdownStep(BaseModel):
    """One actionable step of an issue breakdown."""

    model_config = ConfigDict(extra="ignore")

    order: int = Field(ge=1)
    title: str
    description: str = ""
    files: list[str] = Field(default_factory=list)
    estimated_minutes: int | None = Field(default=None, ge=0)


class IssueBreakdown(BaseModel):
    """Structured understanding of what an issue actually requires."""

    model_config = ConfigDict(extra="ignore")

    issue_id: int | None = None
    summary: str
    difficulty: Difficulty = Field(default=Difficulty.MEDIUM)
    estimated_time: str | None = Field(
        default=None,
        description="Human-readable estimate, e.g. '2-3 hours'.",
    )
    prerequisites: list[str] = Field(default_factory=list)
    skills_required: list[str] = Field(default_factory=list)
    files_to_touch: list[str] = Field(default_factory=list)
    steps: list[BreakdownStep] = Field(default_factory=list)
    acceptance_criteria: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    resources: list[str] = Field(default_factory=list)

    @field_validator("difficulty", mode="before")
    @classmethod
    def _clean_difficulty(cls, value: Any) -> str:
        return _normalize_difficulty(value) or Difficulty.MEDIUM.value


__all__ = [
    "ExperienceLevel",
    "Difficulty",
    "UserSkills",
    "Repository",
    "Issue",
    "IssueDetailResponse",
    "RecommendedIssue",
    "BreakdownStep",
    "IssueBreakdown",
]