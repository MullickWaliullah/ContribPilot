from typing import Literal

from pydantic import BaseModel, Field


class RankingResponse(BaseModel):
    issue_id: int
    match_score: int = Field(..., ge=0, le=100)
    complexity_level: Literal[
        "beginner",
        "intermediate",
        "advanced",
    ]
    is_beginner_friendly: bool
    required_technologies: list[str] = Field(default_factory=list)
    matching_skills: list[str] = Field(default_factory=list)
    missing_or_mismatched_skills: list[str] = Field(default_factory=list)
    reasoning: str = ""


class BreakdownResponse(BaseModel):
    problem_summary: str = ""
    expected_behavior: str = ""
    current_behavior: str = ""
    confirmed_facts: list[str] = Field(default_factory=list)
    files_to_inspect: list[str] = Field(default_factory=list)
    relevant_symbols: list[str] = Field(default_factory=list)
    concepts_to_understand: list[str] = Field(default_factory=list)
    investigation_steps: list[str] = Field(default_factory=list)
    verification_target: str = ""
    context_status: Literal[
        "sufficient",
        "partial",
        "insufficient",
    ] = "insufficient"


class HintResponse(BaseModel):
    level: int = Field(..., ge=1, le=3)
    hint_text: str = Field(..., min_length=1)