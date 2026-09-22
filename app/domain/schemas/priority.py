from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class PolePriorityInput(BaseModel):
    asset_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)
    risk_evaluation_id: str = Field(min_length=1)
    risk_score: float = Field(ge=0, le=100)
    hazard_exposure: float = Field(default=0, ge=0, le=100)
    consequence_score: float = Field(default=0, ge=0, le=100)
    treatment_urgency: float = Field(default=0, ge=0, le=100)
    inspection_confidence: float = Field(default=100, ge=0, le=100)


class PolePriorityResult(BaseModel):
    priority_evaluation_id: str = Field(default_factory=lambda: str(uuid4()))
    asset_id: str
    tenant_id: str
    risk_evaluation_id: str
    priority_score: float = Field(ge=0, le=100)
    priority_band: str
    factors: dict[str, float]
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    rule_version: str

    model_config = {"frozen": True}
