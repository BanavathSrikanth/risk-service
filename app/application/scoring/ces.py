from typing import Any, Dict

from app.domain.schemas.risk_input import ConsequenceInput
from app.application.scoring.rule_loader import load_rules


class CesCalculator:

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        return load_rules(rules_path)

    def calculate(self, data: ConsequenceInput) -> float:

        weights = self.rules["weights"]

        score = (
            data.population_exposure
            * weights["population_exposure"]
            +
            data.critical_infrastructure
            * weights["critical_infrastructure"]
            +
            data.service_impact
            * weights["service_impact"]
        )

        return round(min(100.0, max(0.0, score)), 2)