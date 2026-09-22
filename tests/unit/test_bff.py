import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from bff.main import app
from bff.models import (
    BffEnrichedRiskResponse,
    BffEnrichedFinancialResponse,
    BffEnrichedPriorityResponse,
)

client = TestClient(app)


def test_bff_health_endpoint():
    response = client.get("/bff/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "bff-service"
    assert data["port"] == 8001


@patch("bff.main.bff_service.calculate_risk", new_callable=AsyncMock)
def test_calculate_risk_bff_route(mock_calc):
    mock_calc.return_value = BffEnrichedRiskResponse(
        risk_evaluation_id="eval-123",
        asset_id="POLE-88421",
        tenant_id="PACIFIC-POWER",
        risk_score=78.5,
        risk_category="HIGH",
        category_color="#eab308",
        action_recommendation="Schedule maintenance work within 30 days.",
        confidence=0.95,
        calculated_at="2026-09-22T22:00:00Z",
        factor_scores={"AHS": 80.0, "CES": 70.0, "CQS": 60.0, "DHM": 85.0, "OPS": 75.0, "VES": 65.0},
        drivers=[{"factor": "DHM", "score": 85.0}],
        warnings=[],
    )

    payload = {
        "asset_id": "POLE-88421",
        "tenant_id": "PACIFIC-POWER",
        "age_years": 25.0,
        "material": "wood",
    }
    response = client.post("/bff/api/v1/calculate-risk", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_score"] == 78.5
    assert data["risk_category"] == "HIGH"
    assert data["category_color"] == "#eab308"


@patch("bff.main.bff_service.evaluate_financials", new_callable=AsyncMock)
def test_evaluate_financials_bff_route(mock_eval):
    mock_eval.return_value = BffEnrichedFinancialResponse(
        evaluation_id="fin-999",
        asset_id="POLE-88421",
        tenant_id="PACIFIC-POWER",
        calculation_version="1.0",
        scenarios={},
        base_summary={"net_benefit": 45000.0, "roi": 1.25, "eal": 18000.0},
        investment_recommendation="Favorable net benefit.",
        formatted_net_benefit="$45,000.00",
        formatted_roi="125.0%",
        formatted_eal="$18,000.00",
    )

    payload = {
        "asset_id": "POLE-88421",
        "tenant_id": "PACIFIC-POWER",
        "replacement_cost": 125000.0,
    }
    response = client.post("/bff/api/v1/evaluate-financials", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["formatted_net_benefit"] == "$45,000.00"
    assert data["formatted_roi"] == "125.0%"
