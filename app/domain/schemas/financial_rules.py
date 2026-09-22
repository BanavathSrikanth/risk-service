from typing import Literal

from pydantic import BaseModel, Field

from app.domain.schemas.financial_engine import ConditionBand, HftdTier, ScenarioBands


class FinancialRuleDefaults(BaseModel):
    emergency_replacement_cost: ScenarioBands
    action_cost: ScenarioBands
    customers_affected: ScenarioBands
    outage_duration_hours: ScenarioBands
    outage_cost_per_customer_hour: ScenarioBands
    discount_rate: float = Field(ge=0, lt=1)
    degradation_rate: float = Field(ge=0)
    design_life_years: int = Field(gt=0)
    remaining_life_years: int = Field(ge=0)
    horizon_years: int = Field(gt=0, le=100)
    wildfire_liability_exposure: ScenarioBands


class FinancialRules(BaseModel):
    calculation_version: str = Field(min_length=1)
    currency: Literal["USD"] = "USD"
    failure_probability: dict[ConditionBand, float]
    hftd_ignition_probability: dict[HftdTier, float]
    scenario_multipliers: ScenarioBands
    default_assumptions: FinancialRuleDefaults
