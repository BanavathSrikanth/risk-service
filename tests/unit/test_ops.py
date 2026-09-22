from pathlib import Path

from app.application.scoring.ops import OpsCalculator


def test_ops_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ops.yaml"
    )

    calculator = OpsCalculator(str(rules))

    score = calculator.calculate(
        ahs=80,
        ces=70,
        cqs=60,
    )

    assert score == 100.0


def test_ops_applies_lag_and_scheduled_work_adjustments():
    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ops.yaml"
    )
    calculator = OpsCalculator(str(rules))

    score = calculator.calculate(
        ahs=20,
        ces=20,
        cqs=20,
        days_overdue=30,
        work_already_scheduled=True,
    )

    assert score == 35.0