from app.application.risk_explainability import (
    RiskExplainabilityService,
)


def test_explanation_contains_factors():

    service = RiskExplainabilityService()

    result = service.build_explanation(
        ahs=80,
        ces=70,
        cqs=60,
        dhm=90,
        ops=85,
        ves=75,
        inputs={"asset_id": "A001"},
        calculation_version="1.0",
        confidence=0.95,
    )

    assert "factors" in result
    assert "input_values" in result
    assert result["calculation_version"] == "1.0"
    assert result["confidence"] == 0.95

    assert len(result["factors"]) == 6
    assert any(factor["factor"] == "VES" for factor in result["factors"])