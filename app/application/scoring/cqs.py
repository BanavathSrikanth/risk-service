from typing import Any, Dict

from app.domain.schemas.risk_input import CqsInput
from app.application.scoring.rule_loader import load_rules


class CqsCalculator:

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _normalize(value: float, maximum: float) -> float:
        if maximum <= 0:
            return 0.0

        return min(1.0, value / maximum)

    def calculate(self, data: CqsInput) -> float:

        normalization = self.rules["normalization"]
        weights = self.rules["weights"]

        failure_cost = self._normalize(
            data.failure_cost,
            normalization["failure_cost_max"],
        )

        outage_duration = self._normalize(
            data.outage_duration_hours,
            normalization.get(
                "outage_duration_max",
                normalization["outage_duration_max_hours"],
            ),
        )

        customer_count = self._normalize(
            data.customer_count,
            normalization["customer_count_max"],
        )

        score = (
            failure_cost * weights["failure_cost"]
            + outage_duration * weights["outage_duration"]
            + customer_count * weights["customer_count"]
        )

        return round(score * 100, 2)