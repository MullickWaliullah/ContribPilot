from __future__ import annotations
from typing import Any

import re
import logging

from app.ai.breakdown import breakdown_issue
from app.ai.ranking import rank_issues
from app.ai.hints import generate_hint

from app.schemas.ai import (RankingResponse, BreakdownResponse, HintResponse)

from app.services.github_service import github_services

logger = logging.getLogger(__name__)

