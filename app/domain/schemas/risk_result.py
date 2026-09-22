from datetime import datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class RiskFactorResult(BaseModel):
    score: float = Field(ge=0, le=100)
    contribution: float = Field(ge=0, le=100)


class RiskResult(BaseModel):
    risk_evaluation_id: str = Field(default_factory=lambda: str(uuid4()))
    asset_id: str
    tenant_id: str

    risk_score: float = Field(ge=0, le=100)
    risk_category: str

    ahs: float = Field(ge=0, le=100)
    ces: float = Field(ge=0, le=100)
    cqs: float = Field(ge=0, le=100)
    dhm: float = Field(ge=0, le=100)
    ops: float = Field(ge=0, le=100)
    ves: float = Field(ge=0, le=100)

    calculated_at: datetime
    source_captured_at: datetime
    source_event_id: str = Field(min_length=1)
    calculation_version: str

    input_values: dict[str, Any]
    explanation: dict[str, Any]

    confidence: float = Field(
        default=1.0,
        ge=0,
        le=1,
    )
    stale: bool = False
    warnings: list[str] = Field(default_factory=list)

    model_config = {"frozen": True}