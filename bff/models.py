from typing import Any, Optional
from pydantic import BaseModel, Field


class BffRiskCalculationRequest(BaseModel):
    asset_id: str = Field(..., example="POLE-88421")
    tenant_id: str = Field(..., example="PACIFIC-POWER")
    age_years: float = Field(default=25.0, ge=0)
    material: str = Field(default="wood")
    remaining_fiber_pct: float = Field(default=65.0, ge=0, le=100)
    defect_severity: str = Field(default="major")
    lean_deg: float = Field(default=5.0, ge=0)
    attachment_count: int = Field(default=4, ge=0)
    asset_class: str = Field(default="distribution")
    reinforced_within_10_years: bool = Field(default=False)
    
    # Consequence
    population_exposure: float = Field(default=75.0, ge=0, le=100)
    critical_infrastructure: float = Field(default=60.0, ge=0, le=100)
    service_impact: float = Field(default=70.0, ge=0, le=100)
    
    # Financial Exposure (CQS)
    failure_cost: float = Field(default=450000.0, ge=0)
    outage_duration_hours: float = Field(default=24.0, ge=0)
    customer_count: int = Field(default=3500, ge=0)
    
    # Weather (DHM)
    wind_speed_mph: float = Field(default=42.0, ge=0)
    temperature_f: float = Field(default=98.0)
    relative_humidity_pct: float = Field(default=18.0, ge=0, le=100)
    precipitation_in: float = Field(default=0.0, ge=0)
    fire_weather_index: Optional[float] = Field(default=75.0)
    
    # Operational
    days_overdue: float = Field(default=45.0, ge=0)
    work_already_scheduled: bool = Field(default=False)


class BffFinancialEngineRequest(BaseModel):
    asset_id: str = Field(..., example="POLE-88421")
    tenant_id: str = Field(..., example="PACIFIC-POWER")
    condition_band: str = Field(default="POOR")
    replacement_cost: float = Field(default=125000.0, ge=0)
    customers: int = Field(default=3500, ge=0)
    outage_hours: float = Field(default=24.0, ge=0)
    outage_cost_per_customer_hour: float = Field(default=15.0, ge=0)
    wildfire_liability_exposure: float = Field(default=5000000.0, ge=0)
    hftd_tier: str = Field(default="Tier3")
    action_cost: float = Field(default=35000.0, ge=0)
    remaining_life: float = Field(default=3.0, ge=0)
    design_life: float = Field(default=40.0, ge=1)
    discount_rate: float = Field(default=0.07, ge=0, le=1)
    degradation_rate: float = Field(default=0.05, ge=0, le=1)


class BffPolePriorityRequest(BaseModel):
    asset_id: str = Field(..., example="POLE-88421")
    tenant_id: str = Field(..., example="PACIFIC-POWER")
    composite_risk_score: float = Field(default=82.5, ge=0, le=100)
    consequence_score: float = Field(default=78.0, ge=0, le=100)
    hazard_exposure_score: float = Field(default=85.0, ge=0, le=100)
    days_overdue: float = Field(default=45.0, ge=0)
    inspection_confidence: float = Field(default=0.9, ge=0, le=1)


class BffUnifiedAuditRequest(BaseModel):
    asset_id: str = Field(..., example="POLE-88421")
    tenant_id: str = Field(..., example="PACIFIC-POWER")
    risk_params: Optional[BffRiskCalculationRequest] = None
    financial_params: Optional[BffFinancialEngineRequest] = None


class BffEnrichedRiskResponse(BaseModel):
    risk_evaluation_id: str
    asset_id: str
    tenant_id: str
    risk_score: float
    risk_category: str
    category_color: str
    action_recommendation: str
    confidence: float
    calculated_at: str
    factor_scores: dict[str, float]
    drivers: list[dict[str, Any]]
    warnings: list[str]


class BffEnrichedFinancialResponse(BaseModel):
    evaluation_id: str
    asset_id: str
    tenant_id: str
    calculation_version: str
    scenarios: dict[str, Any]
    base_summary: dict[str, Any]
    investment_recommendation: str
    formatted_net_benefit: str
    formatted_roi: str
    formatted_eal: str


class BffEnrichedPriorityResponse(BaseModel):
    asset_id: str
    tenant_id: str
    priority_score: float
    priority_tier: str
    priority_color: str
    urgency_recommendation: str
    score_breakdown: dict[str, float]


class BffUnifiedAuditResponse(BaseModel):
    asset_id: str
    tenant_id: str
    timestamp: str
    risk: Optional[BffEnrichedRiskResponse] = None
    financials: Optional[BffEnrichedFinancialResponse] = None
    priority: Optional[BffEnrichedPriorityResponse] = None
    history_count: int = 0
    overall_health_status: str
