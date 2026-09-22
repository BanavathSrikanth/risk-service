from pathlib import Path

from app.application.scoring.cqs import CqsCalculator
from app.domain.schemas.risk_input import CqsInput


def test_cqs_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "cqs.yaml"
    )

    calculator = CqsCalculator(str(rules))

    data = CqsInput(
        failure_cost=500_000,
        outage_duration_hours=36,
        customer_count=5_000,
    )

    score = calculator.calculate(data)

    assert score == 50.0