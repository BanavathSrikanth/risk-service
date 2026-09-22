from app.application.pole_prioritization import PolePriorityService
from app.domain.schemas.priority import PolePriorityInput


def test_pole_priority_is_separate_from_risk_authority():
    result = PolePriorityService().calculate(
        PolePriorityInput(
            asset_id="pole-1",
            tenant_id="tenant-1",
            risk_evaluation_id="risk-1",
            risk_score=90,
            hazard_exposure=80,
            consequence_score=70,
            treatment_urgency=60,
            inspection_confidence=100,
        )
    )

    assert result.priority_score == 81.0
    assert result.priority_band == "high"
    assert result.risk_evaluation_id == "risk-1"
    assert result.rule_version == "pole-priority-1.0"
