from pathlib import Path

from app.domain.entities.risk_result import RiskResult
from app.application.scoring.rule_loader import load_rules
from app.infrastructure.repositories.risk_repository import RiskRepository


class RiskCalculationService:
    def __init__(self, repository: RiskRepository):
        self.repository = repository
        rules_path = Path(__file__).parents[2] / "domain" / "rules" / "v1" / "risk.yaml"
        self.weights = load_rules(str(rules_path))["weights"]

    def calculate(
        self,
        asset_id: str,
        tenant_id: str,
        ahs: float,
        ces: float,
        cqs: float,
        dhm: float,
        ops: float,
        ves: float = 0.0,
    ) -> RiskResult:
        risk_score = (
            ahs * self.weights["ahs"]
            + ces * self.weights["ces"]
            + cqs * self.weights["cqs"]
            + dhm * self.weights["dhm"]
            + ops * self.weights["ops"]
            + ves * self.weights["ves"]
        )
        risk_score = max(0.0, min(100.0, risk_score))
        risk_score = round(risk_score, 2)

        if risk_score >= 90:
            risk_category = "critical"
        elif risk_score >= 70:
            risk_category = "high"
        elif risk_score >= 40:
            risk_category = "medium"
        else:
            risk_category = "low"

        result = RiskResult.create(
            asset_id=asset_id,
            tenant_id=tenant_id,
            risk_score=risk_score,
            ves=max(0.0, min(100.0, ves)),
            risk_category=risk_category,
            drivers={
                "ahs": ahs,
                "ces": ces,
                "cqs": cqs,
                "dhm": dhm,
                "ops": ops,
                "ves": ves,
            },
        )
        return self.repository.save(result)
