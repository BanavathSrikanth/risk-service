from pathlib import Path

from app.application.scoring.ces import CesCalculator
from app.domain.schemas.risk_input import ConsequenceInput


def test_ces_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ces.yaml"
    )

    calculator = CesCalculator(str(rules))

    data = ConsequenceInput(
        population_exposure=80,
        critical_infrastructure=60,
        service_impact=70,
    )

    score = calculator.calculate(data)

    assert score == 71.5