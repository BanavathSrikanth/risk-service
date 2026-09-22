from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import yaml

from app.domain.schemas.financial_engine import (
    ConditionBand,
    FinancialEngineInput,
    FinancialEngineResult,
    FinancialScenarioResult,
    ScenarioName,
)
from app.domain.schemas.financial_rules import FinancialRules


@dataclass(frozen=True)
class _ScenarioValues:
    replacement_cost: float
    action_cost: float
    customers: float
    outage_hours: float
    outage_rate: float
    liability: float
    probability_multiplier: float


class FinancialEngine:
    """Deterministic three-scenario avoided-loss and ROI calculator."""

    def __init__(self, rules_path: str | None = None) -> None:
        path = Path(rules_path) if rules_path else (
            Path(__file__).parents[1] / "domain" / "rules" / "v1" / "financial.yaml"
        )
        with path.open("r", encoding="utf-8") as file:
            self.rules = FinancialRules.model_validate(yaml.safe_load(file))
        self.calculation_version = self.rules.calculation_version

    def calculate(
        self, request: FinancialEngineInput, *, currency: str | None = None
    ) -> FinancialEngineResult:
        request = self._with_rule_defaults(request)
        scenario_names: tuple[ScenarioName, ...] = ("low", "base", "high")
        scenarios = [
            self._calculate_scenario(request, name) for name in scenario_names
        ]
        return FinancialEngineResult(
            roi_evaluation_id=str(uuid4()),
            tenant_id=request.tenant_id,
            asset_id=request.asset_id,
            assumption_version=request.assumption_version,
            risk_evaluation_id=request.risk_evaluation_id,
            currency=currency or self.rules.currency,
            status="calculated",
            scenarios=scenarios,
            inputs_snapshot=request.model_dump(mode="json"),
            calculation_version=self.calculation_version,
        )

    def _with_rule_defaults(
        self, request: FinancialEngineInput
    ) -> FinancialEngineInput:
        defaults = self.rules.default_assumptions.model_dump()
        values = request.model_dump()
        for field, value in defaults.items():
            if values[field] is None:
                values[field] = value
        if values["failure_probability_multipliers"] is None:
            values["failure_probability_multipliers"] = (
                self.rules.scenario_multipliers.model_dump()
            )
        return FinancialEngineInput.model_validate(values)

    def _calculate_scenario(
        self, request: FinancialEngineInput, name: ScenarioName
    ) -> FinancialScenarioResult:
        assert request.wildfire_liability_exposure is not None
        assert request.emergency_replacement_cost is not None
        assert request.action_cost is not None
        assert request.customers_affected is not None
        assert request.outage_duration_hours is not None
        assert request.outage_cost_per_customer_hour is not None
        assert request.failure_probability_multipliers is not None
        assert request.design_life_years is not None
        assert request.remaining_life_years is not None
        assert request.horizon_years is not None
        assert request.discount_rate is not None
        assert request.degradation_rate is not None
        values = _ScenarioValues(
            replacement_cost=getattr(request.emergency_replacement_cost, name),
            action_cost=getattr(request.action_cost, name),
            customers=getattr(request.customers_affected, name),
            outage_hours=getattr(request.outage_duration_hours, name),
            outage_rate=getattr(request.outage_cost_per_customer_hour, name),
            liability=getattr(request.wildfire_liability_exposure, name),
            probability_multiplier=getattr(request.failure_probability_multipliers, name),
        )
        current_probability = self._failure_probability(
            request.condition_band, request.ces, values.probability_multiplier
        )
        post_action_probability = self._failure_probability(
            request.post_action_condition_band,
            request.post_action_ces,
            values.probability_multiplier,
        )
        consequence = self._consequence(request, values)
        current_eal = current_probability * consequence
        defer_cost = self._present_value(
            current_probability, consequence, request
        )
        act_cost = self._present_value(
            post_action_probability, consequence, request
        )
        residual_value = values.replacement_cost * (
            request.remaining_life_years / request.design_life_years
        )
        avoided_loss = defer_cost - act_cost
        net_benefit = avoided_loss - values.action_cost - residual_value
        roi = (
            net_benefit / values.action_cost
            if values.action_cost > 0
            else None
        )
        break_even = self._break_even_year(
            current_probability,
            post_action_probability,
            consequence,
            values.action_cost + residual_value,
            request,
        )
        return FinancialScenarioResult(
            scenario=name,
            failure_probability_annual=current_probability,
            consequence_cost=consequence,
            expected_annual_loss=current_eal,
            cost_of_inaction=defer_cost,
            residual_value_destroyed=residual_value,
            avoided_loss=avoided_loss,
            net_benefit=net_benefit,
            roi=roi,
            break_even_year=break_even,
        )

    def _failure_probability(
        self,
        condition_band: ConditionBand, ces: float, multiplier: float
    ) -> float:
        return (
            self.rules.failure_probability[condition_band]
            * (1 + ces / 100)
            * multiplier
        )

    def _consequence(
        self,
        request: FinancialEngineInput, values: _ScenarioValues
    ) -> float:
        ignition_probability = self.rules.hftd_ignition_probability[request.hftd_tier]
        outage_cost = values.customers * values.outage_hours * values.outage_rate
        return (
            values.replacement_cost
            + outage_cost
            + ignition_probability * values.liability
        )

    @staticmethod
    def _present_value(
        probability: float, consequence: float, request: FinancialEngineInput
    ) -> float:
        assert request.horizon_years is not None
        assert request.degradation_rate is not None
        assert request.discount_rate is not None
        total = 0.0
        for year in range(1, request.horizon_years + 1):
            escalated_probability = probability * (
                1 + request.degradation_rate
            ) ** (year - 1)
            total += (
                escalated_probability
                * consequence
                / (1 + request.discount_rate) ** year
            )
        return total

    @staticmethod
    def _break_even_year(
        current_probability: float,
        post_action_probability: float,
        consequence: float,
        action_cost: float,
        request: FinancialEngineInput,
    ) -> int | None:
        assert request.horizon_years is not None
        assert request.degradation_rate is not None
        assert request.discount_rate is not None
        cumulative = 0.0
        for year in range(1, request.horizon_years + 1):
            current = current_probability * (
                1 + request.degradation_rate
            ) ** (year - 1)
            post_action = post_action_probability * (
                1 + request.degradation_rate
            ) ** (year - 1)
            cumulative += (current - post_action) * consequence / (
                1 + request.discount_rate
            ) ** year
            if cumulative >= action_cost:
                return year
        return None
