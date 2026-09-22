from pathlib import Path

from app.application.scoring.dhm import DhmCalculator
from app.domain.schemas.risk_input import WeatherInput


def test_dhm_calculation():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "dhm.yaml"
    )

    calculator = DhmCalculator(str(rules))

    weather = WeatherInput(
        wind_speed_mph=35,
        temperature_f=100,
        relative_humidity_pct=15,
        precipitation_in=0,
        fire_weather_index=80,
    )

    score = calculator.calculate(weather)

    assert 0 <= score <= 100