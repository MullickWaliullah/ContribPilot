"""
Schemas for the sandbox verification flow:

    reproduce -> generate-patch -> apply-patch -> run
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TestStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"       # collection error / import error
    TIMEOUT = "timeout"


class VerificationPhase(str, Enum):
    REPRODUCE = "reproduce"
    APPLY_PATCH = "apply-patch"
    RUN = "run"


# --------------------------------------------------------------------------- #
# Test result
# --------------------------------------------------------------------------- #

class TestResult(BaseModel):
    """Outcome of a single pytest run inside the sandbox."""

    model_config = ConfigDict(extra="ignore")

    status: TestStatus
    passed: int = Field(default=0, ge=0)
    failed: int = Field(default=0, ge=0)
    total: int = Field(default=0, ge=0)
    stdout: str = ""
    stderr: str = ""
    duration: float = Field(default=0.0, ge=0.0, description="Seconds.")

    @model_validator(mode="after")
    def _fill_total(self) -> "TestResult":
        if self.total == 0 and (self.passed or self.failed):
            self.total = self.passed + self.failed
        return self

    @property
    def is_green(self) -> bool:
        """True only for a clean, fully passing run."""
        return self.status is TestStatus.PASSED


# --------------------------------------------------------------------------- #
# Requests
# --------------------------------------------------------------------------- #

class VerificationRequest(BaseModel):
    """
    Body for `POST /api/verification/reproduce` and
    `POST /api/verification/run`.

    There is deliberately no `command` field. The sandbox decides what
    to execute; callers may only narrow it to a specific test path.
    """

    model_config = ConfigDict(extra="forbid")

    issue_id: int
    contribution_id: str | None = None
    workspace_id: str | None = Field(
        default=None,
        description="Existing workspace; created if omitted.",
    )
    test_path: str | None = Field(
        default=None,
        description="Optional relative test path, e.g. 'tests/test_cli.py'.",
        examples=["tests/test_cli.py"],
    )
    timeout: int = Field(
        default=120,
        ge=5,
        le=600,
        description="Hard execution timeout in seconds.",
    )

    @field_validator("test_path")
    @classmethod
    def _safe_test_path(cls, value: str | None) -> str | None:
        if value is None:
            return None
        token = value.strip().replace("\\", "/")
        if not token:
            return None
        if token.startswith(("/", "~")) or ".." in token.split("/"):
            raise ValueError("test_path must be a relative path inside the workspace")
        return token


class PatchRequest(BaseModel):
    """Body for `POST /api/verification/apply-patch`."""

    model_config = ConfigDict(extra="forbid")

    issue_id: int
    patch: str = Field(description="Unified diff produced by generate-patch.")
    contribution_id: str | None = None
    workspace_id: str | None = None
    dry_run: bool = Field(
        default=False,
        description="Validate the patch without writing it to the workspace.",
    )


# --------------------------------------------------------------------------- #
# Responses
# --------------------------------------------------------------------------- #

class VerificationResponse(BaseModel):
    """
    Body for `POST /api/verification/reproduce` and
    `POST /api/verification/run`.
    """

    model_config = ConfigDict(extra="ignore")

    issue_id: int
    contribution_id: str | None = None
    workspace_id: str
    phase: VerificationPhase
    result: TestResult
    message: str | None = Field(
        default=None,
        description="Human-readable summary, e.g. 'RED: 2 failing tests'.",
    )
    generated_at: datetime = Field(default_factory=_utcnow)


class PatchApplyResponse(BaseModel):
    """Body for `POST /api/verification/apply-patch`."""

    model_config = ConfigDict(extra="ignore")

    issue_id: int
    contribution_id: str | None = None
    workspace_id: str
    applied: bool
    changed_files: list[str] = Field(default_factory=list)
    diff: str = Field(default="", description="Diff actually written to disk.")
    message: str | None = None
    generated_at: datetime = Field(default_factory=_utcnow)


__all__ = [
    "TestStatus",
    "VerificationPhase",
    "TestResult",
    "VerificationRequest",
    "VerificationResponse",
    "PatchRequest",
    "PatchApplyResponse",
]