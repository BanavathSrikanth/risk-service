from typing import Any, Dict

from app.domain.schemas.risk_input import WeatherInput
from app.application.scoring.rule_loader import load_rules


class DhmCalculator:

    def __init__(self, rules_path: str):
        self.rules = self._load_rules(rules_path)

    @staticmethod
    def _load_rules(rules_path: str) -> Dict[str, Any]:
        return load_rules(rules_path)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(100.0, value))

    def calculate(self, weather: WeatherInput) -> float:

        thresholds = self.rules["thresholds"]
        weights = self.rules["weights"]

        wind_high = thresholds["wind_speed_mph"]["high"]
        wind_score = self._clamp(
            weather.wind_speed_mph / wind_high * 100
        )

        temp_high = thresholds["temperature_f"]["high"]
        temperature_score = self._clamp(
            max(0.0, weather.temperature_f - 70)
            / max(1.0, temp_high - 70)
            * 100
        )

        humidity_score = self._clamp(
            (50 - weather.relative_humidity_pct)
            / 35
            * 100
        )

        precipitation_score = self._clamp(
            weather.precipitation_in / 2 * 100
        )

        fire_weather_score = (
            weather.fire_weather_index
            if weather.fire_weather_index is not None
            else 0.0
        )

        score = (
            wind_score * weights["wind"]
            + temperature_score * weights["temperature"]
            + humidity_score * weights["humidity"]
            + precipitation_score * weights["precipitation"]
            + fire_weather_score * weights["fire_weather"]
        )

        return round(self._clamp(score), 2)