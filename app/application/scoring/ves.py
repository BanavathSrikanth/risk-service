from typing import Any

from app.domain.schemas.risk_input import InspectionInput
from app.application.scoring.rule_loader import load_rules


class VesCalculator:
    """Calculate Vulnerability Exposure Severity from configured weights."""

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, value))

    def calculate(
        self,
        *,
        ahs: float,
        consequence: float,
        inspection: InspectionInput,
    ) -> float:
        weights = self.rules["weights"]
        evidence_factor = min(
            1.0,
            inspection.evidence_count / self.rules["normalization"]["evidence_count_max"],
        )
        score = (
            ahs * weights["asset_condition"]
            + consequence * weights["consequence"]
            + inspection.exposure_level * weights["exposure"]
            + inspection.severity * weights["severity"]
            + evidence_factor * 100 * weights["evidence"]
        )
        return round(self._clamp(score), 2)
