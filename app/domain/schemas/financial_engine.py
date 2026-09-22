from typing import Literal

from pydantic import BaseModel, Field, model_validator


ConditionBand = Literal["excellent", "good", "fair", "poor", "critical"]
HftdTier = Literal["tier1", "tier2", "tier3", "none"]
ScenarioName = Literal["low", "base", "high"]


class ScenarioBands(BaseModel):
    low: float = Field(ge=0)
    base: float = Field(ge=0)
    high: float = Field(ge=0)

    @model_validator(mode="after")
    def ordered(self) -> "ScenarioBands":
        if not self.low <= self.base <= self.high:
            raise ValueError("scenario bands must be ordered low <= base <= high")
        return self


class FinancialEngineInput(BaseModel):
    tenant_id: str = Field(min_length=1)
    asset_id: str = Field(min_length=1)
    assumption_version: str = Field(min_length=1)
    risk_evaluation_id: str | None = None

    condition_band: ConditionBand
    ces: float = Field(ge=0, le=100)
    hftd_tier: HftdTier = "none"
    wildfire_liability_exposure: ScenarioBands | None = None

    emergency_replacement_cost: ScenarioBands | None = None
    action_cost: ScenarioBands | None = None
    customers_affected: ScenarioBands | None = None
    outage_duration_hours: ScenarioBands | None = None
    outage_cost_per_customer_hour: ScenarioBands | None = None

    post_action_condition_band: ConditionBand
    post_action_ces: float = Field(ge=0, le=100)
    design_life_years: int | None = Field(default=None, gt=0)
    remaining_life_years: int | None = Field(default=None, ge=0)
    horizon_years: int | None = Field(default=None, gt=0, le=100)
    discount_rate: float | None = Field(default=None, ge=0, lt=1)
    degradation_rate: float | None = Field(default=None, ge=0)
    failure_probability_multipliers: ScenarioBands | None = None

    @model_validator(mode="after")
    def validate_life(self) -> "FinancialEngineInput":
        if (
            self.remaining_life_years is not None
            and self.design_life_years is not None
            and self.remaining_life_years > self.design_life_years
        ):
            raise ValueError("remaining_life_years cannot exceed design_life_years")
        if (
            self.hftd_tier != "none"
            and self.wildfire_liability_exposure is not None
            and self.wildfire_liability_exposure.base <= 0
        ):
            raise ValueError(
                "wildfire_liability_exposure is required for high fire threat areas"
            )
        return self


class FinancialScenarioResult(BaseModel):
    scenario: ScenarioName
    failure_probability_annual: float
    consequence_cost: float
    expected_annual_loss: float
    cost_of_inaction: float
    residual_value_destroyed: float
    avoided_loss: float
    net_benefit: float
    roi: float | None
    break_even_year: int | None


class FinancialEngineResult(BaseModel):
    roi_evaluation_id: str
    tenant_id: str
    asset_id: str
    assumption_version: str
    risk_evaluation_id: str | None = None
    currency: str
    status: Literal["calculated", "insufficient_data"]
    scenarios: list[FinancialScenarioResult]
    inputs_snapshot: dict[str, object]
    calculation_version: str
