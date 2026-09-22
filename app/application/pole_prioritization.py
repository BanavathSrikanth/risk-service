from app.domain.schemas.priority import PolePriorityInput, PolePriorityResult


class PolePriorityService:
    """Ranks work candidates; it does not authorize work or replace assets."""

    rule_version = "pole-priority-1.0"
    weights = {
        "risk_score": 0.40,
        "hazard_exposure": 0.25,
        "consequence_score": 0.20,
        "treatment_urgency": 0.10,
        "inspection_confidence": 0.05,
    }

    def calculate(self, data: PolePriorityInput) -> PolePriorityResult:
        factors = {
            "risk_score": data.risk_score,
            "hazard_exposure": data.hazard_exposure,
            "consequence_score": data.consequence_score,
            "treatment_urgency": data.treatment_urgency,
            "inspection_confidence": data.inspection_confidence,
        }
        score = round(
            sum(factors[name] * weight for name, weight in self.weights.items()),
            2,
        )
        if score >= 90:
            band = "critical"
        elif score >= 70:
            band = "high"
        elif score >= 40:
            band = "medium"
        else:
            band = "low"

        return PolePriorityResult(
            asset_id=data.asset_id,
            tenant_id=data.tenant_id,
            risk_evaluation_id=data.risk_evaluation_id,
            priority_score=score,
            priority_band=band,
            factors=factors,
            rule_version=self.rule_version,
        )
