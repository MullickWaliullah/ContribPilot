from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.issues import router as issues_router
from app.api.contributions import router as contributions_router
from app.ai.llm_client import LLMAuthError, LLMRateLimitError
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


app = FastAPI(
    title="ContribPilot API",
    description=(
        "AI-Powered GitHub contribution assistant"
        "for issue discovery, breakdown and guided hints."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    issues_router,
    prefix="/api/issues",
    tags=["Issues"],
)

app.include_router(
    contributions_router,
    prefix="/api/contributions",
    tags=["Contributions"],
)


@app.get(
    "/health",
    tags=["Health"],
)
def health_check():
    return {
        "status": "ok",
        "service": "ContribPilot API",
    }


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    return JSONResponse(
        status_code=422,
        content={
            "error": "ValidationError",
            "message": "Invalid request data.",
            "details": exc.errors(),
        },
    )


@app.exception_handler(LLMAuthError)
async def llm_auth_exception_handler(
    request: Request,
    exc: LLMAuthError,
):
    return JSONResponse(
        status_code=401,
        content={
            "error": "InvalidLLMKey",
            "message": str(exc),
        },
    )


@app.exception_handler(LLMRateLimitError)
async def llm_rate_limit_exception_handler(
    request: Request,
    exc: LLMRateLimitError,
):
    return JSONResponse(
        status_code=429,
        content={
            "error": "LLMRateLimited",
            "message": str(exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "message": "An unexpected server error occurred.",
        },
    )