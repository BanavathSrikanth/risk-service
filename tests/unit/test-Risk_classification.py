from pathlib import Path

from app.application.risk_classification import RiskClassifier


def test_risk_classification():

    rules = (
        Path(__file__).parents[3]
        / "app"
        / "domain"
        / "rules"
        / "v1"
        / "risk.yaml"
    )

    classifier = RiskClassifier(str(rules))

    assert classifier.classify(10) == "LOW"
    assert classifier.classify(30) == "MODERATE"
    assert classifier.classify(50) == "HIGH"
    assert classifier.classify(70) == "VERY_HIGH"
    assert classifier.classify(90) == "CRITICAL"