from typing import Literal

from pydantic import BaseModel, Field

from app.schemas.ai import (
    RankingResponse,
    BreakdownResponse,
)



ExperienceLevel = Literal[
    "beginner",
    "intermediate",
    "advanced",
]



class RecommendRequest(BaseModel):

    skills: list[str] = Field(
        ...,
        min_length=1,
        description="User skills, e.g. ['python', 'pytest']",
    )

    experience: ExperienceLevel = Field(
        ...,
        description="User experience level",
    )

    repo: str = Field(
        ...,
        description="GitHub repository in owner/repo format",
    )

    limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of issues to return",
    )


class RecommendResponse(BaseModel):

    issues: list[RankingResponse]

    total: int

    repo: str


class BreakdownRequest(BaseModel):
    repo: str = Field(
        ...,
        description="GitHub repository in owner/repo format",
    )

    skills: list[str] = Field(
        ...,
        min_length=1,
        description="User skills",
    )

    experience: ExperienceLevel = Field(
        ...,
        description="User experience level",
    )


class BreakdownWrapper(BaseModel):

    issue_id: int

    repo: str

    breakdown: BreakdownResponse



class HintRequest(BaseModel):
    
    level: int = Field(
        ...,
        ge=1,
        le=3,
        description="Hint level: 1, 2, or 3",
    )

    issue_context: dict = Field(
        ...,
        description="Issue and repository context",
    )

    current_progress: dict = Field(
        ...,
        description="Previously shown hints and progress",
    )