from pathlib import Path

from app.application.risk_calculation import (
    RiskCalculationService,
)
from app.domain.schemas.risk_input import (
    AhsInput,
    ConsequenceInput,
    CqsInput,
    RiskInput,
    WeatherInput,
)


def test_complete_risk_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
    )

    service = RiskCalculationService(str(rules))

    input_data = RiskInput(
        asset_id="ASSET-001",
        tenant_id="TENANT-001",

        ahs=AhsInput(
            age_years=20,
            material="wood",
            remaining_fiber_pct=70,
            defect_severity="major",
            lean_deg=4,
            attachment_count=6,
            asset_class="distribution",
            reinforced_within_10_years=True,
        ),

        consequence=ConsequenceInput(
            population_exposure=80,
            critical_infrastructure=60,
            service_impact=70,
        ),

        cqs=CqsInput(
            failure_cost=500_000,
            outage_duration_hours=36,
            customer_count=5_000,
        ),

        weather=WeatherInput(
            wind_speed_mph=35,
            temperature_f=100,
            relative_humidity_pct=15,
            precipitation_in=0,
            fire_weather_index=80,
        ),

        time_sensitivity=60,
    )

    result = service.calculate(input_data)

    assert result.asset_id == "ASSET-001"
    assert result.tenant_id == "TENANT-001"

    assert 0 <= result.risk_score <= 100

    assert result.risk_category in {
        "LOW",
        "MODERATE",
        "HIGH",
        "VERY_HIGH",
        "CRITICAL",
    }

    assert result.ahs >= 0
    assert result.ces >= 0
    assert result.cqs >= 0
    assert result.dhm >= 0
    assert result.ops >= 0

    assert result.calculation_version == "1.1"

    weights = service.classifier.weights
    expected_score = round(
        min(
            100.0,
            result.ahs * weights["ahs"]
            + result.ces * weights["ces"]
            + result.cqs * weights["cqs"]
            + result.dhm * weights["dhm"]
            + result.ops * weights["ops"]
            + result.ves * weights["ves"],
        ),
        2,
    )
    assert result.risk_score == expected_score
    assert any(
        factor["factor"] == "VES"
        for factor in result.explanation["factors"]
    )

    assert result.input_values is not None
    assert result.explanation is not None
    assert result.confidence == 1.0

    stale_result = service.calculate(
        input_data.model_copy(
            update={
                "stale_feeds": ["AHS"],
                "imputed_feeds": ["VES"],
                "missing_feeds": ["CQS"],
                "critical_missing_feeds": ["CQS"],
            }
        )
    )
    assert stale_result.confidence == 0.12
    assert stale_result.warnings == ["Critical input missing: CQS"]
    assert stale_result.risk_score == result.risk_score