from typing import Any, Dict

from app.domain.schemas.risk_input import AhsInput
from app.application.scoring.rule_loader import load_rules


class AhsCalculator:

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
        return max(minimum, min(value, maximum))

    def calculate(self, data: AhsInput) -> float:

        design_life = self.rules["design_life_years"][data.material]

        age_factor = self._clamp(
            data.age_years / design_life
        )

        decay_factor = 1.0 - (
            data.remaining_fiber_pct / 100.0
        )

        defect_factor = self.rules["defect_weights"][
            data.defect_severity
        ]

        lean_factor = self._clamp(
            data.lean_deg / 10.0
        )

        max_attachments = self.rules["max_attachments"][
            data.asset_class
        ]

        load_factor = self._clamp(
            data.attachment_count / max_attachments
        )

        reinforcement_credit = (
            self.rules["reinforcement"]["credit"]
            if data.reinforced_within_10_years
            else 0.0
        )

        weights = self.rules["weights"]

        normalized_score = (
            weights["age"] * age_factor
            + weights["decay"] * decay_factor
            + weights["defect"] * defect_factor
            + weights["lean"] * lean_factor
            + weights["load"] * load_factor
            - reinforcement_credit
        )

        normalized_score = self._clamp(normalized_score)

        return round(normalized_score * 100, 2)