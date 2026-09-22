from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WeatherInput(BaseModel):
    wind_speed_mph: float = Field(default=0.0, ge=0)
    temperature_f: float = Field(default=70.0)
    relative_humidity_pct: float = Field(default=50.0, ge=0, le=100)
    precipitation_in: float = Field(default=0.0, ge=0)
    fire_weather_index: Optional[float] = Field(default=None, ge=0, le=100)

    observed_at: Optional[datetime] = None
    source: Optional[str] = None


class AhsInput(BaseModel):
    age_years: float = Field(ge=0)
    material: str
    remaining_fiber_pct: float = Field(ge=0, le=100)
    defect_severity: str
    lean_deg: float = Field(default=0.0, ge=0)
    attachment_count: int = Field(default=0, ge=0)
    asset_class: str
    reinforced_within_10_years: bool = False


class ConsequenceInput(BaseModel):
    population_exposure: float = Field(default=0, ge=0, le=100)
    critical_infrastructure: float = Field(default=0, ge=0, le=100)
    service_impact: float = Field(default=0, ge=0, le=100)


class CqsInput(BaseModel):
    failure_cost: float = Field(default=0, ge=0)
    outage_duration_hours: float = Field(default=0, ge=0)
    customer_count: int = Field(default=0, ge=0)


class InspectionInput(BaseModel):
    exposure_level: float = Field(default=0, ge=0, le=100)
    severity: float = Field(default=0, ge=0, le=100)
    evidence_count: int = Field(default=0, ge=0)


class HazardExposureInput(BaseModel):
    hazard_type: str = Field(min_length=1)
    exposure_score: float = Field(ge=0, le=100)
    layer_snapshot_id: str = Field(min_length=1)
    source_observed_at: datetime
    source: str = Field(min_length=1)


class RiskInput(BaseModel):
    asset_id: str = Field(min_length=1)
    tenant_id: str = Field(min_length=1)

    calculated_at: Optional[datetime] = None

    ahs: AhsInput
    consequence: ConsequenceInput
    cqs: CqsInput

    weather: WeatherInput = Field(
        default_factory=WeatherInput
    )

    time_sensitivity: float = Field(
        default=0,
        ge=0,
        le=100,
    )
    days_overdue: float = Field(default=0, ge=0)
    work_already_scheduled: bool = False
    stale_feeds: list[str] = Field(default_factory=list)
    imputed_feeds: list[str] = Field(default_factory=list)
    missing_feeds: list[str] = Field(default_factory=list)
    critical_missing_feeds: list[str] = Field(default_factory=list)

    inspection: InspectionInput = Field(default_factory=InspectionInput)

    hazard_exposures: list[HazardExposureInput] = Field(default_factory=list)