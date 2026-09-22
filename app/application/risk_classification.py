from typing import Any

from app.application.scoring.rule_loader import load_rules


class RiskClassifier:

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> dict[str, Any]:
        return load_rules(rules_path)

    @property
    def weights(self) -> dict[str, float]:
        return self.rules["weights"]

    def classify(self, risk_score: float) -> str:
        score = max(0.0, min(100.0, risk_score))

        for category in self.rules["classification"]["categories"]:
            if (
                category["min_score"]
                <= score
                < category["max_score"]
            ):
                return category["name"]

        # Include 100 in the final category.
        last_category = self.rules["classification"]["categories"][-1]

        if score == last_category["max_score"]:
            return last_category["name"]

        raise ValueError(
            f"Risk score {score} does not match a configured category."
        )