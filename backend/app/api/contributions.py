from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException

from app.schemas.request import HintRequest
from app.schemas.ai import HintResponse
from app.services import ai_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/hint",
    response_model=HintResponse,
    )
def get_hint(request: HintRequest ) -> HintResponse:
    try:
        return ai_service.get_hint(
            level=request.level,
            issue_context=request.issue_context,
            current_progress=request.current_progress,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc) or "Invalid hint request.",
        ) from exc
    except RuntimeError as exc:
        logger.exception(
            "Hint generation failed: %s", exc,
        )

        raise HTTPException(
            status_code=502,
            detail=str(exc) or "Failed to generate hint.",
        ) from exc
    except Exception as exc:
        logger.exception(
            "Unexpected hint API error: %s",
            exc,
        )

        raise HTTPException(
            status_code=500,
            detail="Internal server error.",
        ) from exc

    