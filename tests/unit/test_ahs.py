from pathlib import Path

from app.application.scoring.ahs import AhsCalculator
from app.domain.schemas.risk_input import AhsInput


def test_ahs_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "ahs.yaml"
    )

    calculator = AhsCalculator(str(rules))

    data = AhsInput(
        age_years=20,
        material="wood",
        remaining_fiber_pct=70,
        defect_severity="major",
        lean_deg=4,
        attachment_count=6,
        asset_class="distribution",
        reinforced_within_10_years=True,
    )

    score = calculator.calculate(data)

    assert score == 34.25