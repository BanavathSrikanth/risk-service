import pytest

from app.application.financial_engine import FinancialEngine
from app.domain.schemas.financial_engine import FinancialEngineInput


def request(**overrides: object) -> FinancialEngineInput:
    values = {
        "tenant_id": "tenant-a",
        "asset_id": "pole-1",
        "assumption_version": "cost-input-2026-01",
        "condition_band": "poor",
        "ces": 80,
        "hftd_tier": "tier3",
        "wildfire_liability_exposure": {"low": 500_000_000, "base": 1_000_000_000, "high": 2_000_000_000},
        "emergency_replacement_cost": {"low": 15_000, "base": 25_000, "high": 35_000},
        "action_cost": {"low": 15_000, "base": 25_000, "high": 35_000},
        "customers_affected": {"low": 100, "base": 200, "high": 300},
        "outage_duration_hours": {"low": 2, "base": 4, "high": 8},
        "outage_cost_per_customer_hour": {"low": 5, "base": 10, "high": 20},
        "post_action_condition_band": "good",
        "post_action_ces": 20,
        "design_life_years": 50,
        "remaining_life_years": 20,
        "horizon_years": 10,
        "discount_rate": 0.05,
        "degradation_rate": 0.02,
    }
    values.update(overrides)
    return FinancialEngineInput.model_validate(values)


def test_engine_returns_all_scenarios_and_snapshot() -> None:
    result = FinancialEngine().calculate(request())

    assert [scenario.scenario for scenario in result.scenarios] == [
        "low",
        "base",
        "high",
    ]
    assert result.inputs_snapshot["assumption_version"] == "cost-input-2026-01"
    assert all(scenario.consequence_cost > 0 for scenario in result.scenarios)


def test_early_replacement_can_have_negative_roi() -> None:
    result = FinancialEngine().calculate(
        request(
            condition_band="excellent",
            ces=0,
            hftd_tier="none",
            post_action_condition_band="excellent",
            post_action_ces=0,
            action_cost={"low": 100_000, "base": 100_000, "high": 100_000},
            emergency_replacement_cost={"low": 15_000, "base": 25_000, "high": 35_000},
        )
    )

    assert result.scenarios[1].net_benefit < 0
    assert result.scenarios[1].roi is not None
    assert result.scenarios[1].roi < 0


def test_missing_liability_for_fire_area_is_rejected() -> None:
    with pytest.raises(ValueError, match="wildfire_liability_exposure"):
        request(
            hftd_tier="tier3",
            wildfire_liability_exposure={"low": 0, "base": 0, "high": 0},
        )


def test_life_boundary_is_enforced() -> None:
    with pytest.raises(ValueError, match="remaining_life_years"):
        request(design_life_years=10, remaining_life_years=11)


def test_sme_yaml_supplies_financial_defaults() -> None:
    result = FinancialEngine().calculate(
        request(
            wildfire_liability_exposure=None,
            emergency_replacement_cost=None,
            action_cost=None,
            customers_affected=None,
            outage_duration_hours=None,
            outage_cost_per_customer_hour=None,
            design_life_years=None,
            remaining_life_years=None,
            horizon_years=None,
            discount_rate=None,
            degradation_rate=None,
            failure_probability_multipliers=None,
        )
    )

    assert result.currency == "USD"
    assert result.calculation_version == "financial-engine-v2"
    assert result.inputs_snapshot["discount_rate"] == 0.05
    assert result.inputs_snapshot["failure_probability_multipliers"] == {
        "low": 0.8,
        "base": 1.0,
        "high": 1.2,
    }
