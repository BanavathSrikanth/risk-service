import os
import logging
from typing import Any, Dict, Optional
import httpx

from bff.models import (
    BffRiskCalculationRequest,
    BffFinancialEngineRequest,
    BffPolePriorityRequest,
    BffEnrichedRiskResponse,
    BffEnrichedFinancialResponse,
    BffEnrichedPriorityResponse,
    BffUnifiedAuditResponse,
)

logger = logging.getLogger("bff.service")

BACKEND_SERVICE_URL = os.getenv("BACKEND_SERVICE_URL", "http://localhost:8000")


class BffService:
    def __init__(self, backend_url: str = BACKEND_SERVICE_URL):
        self.backend_url = backend_url.rstrip("/")

    async def calculate_risk(self, req: BffRiskCalculationRequest) -> BffEnrichedRiskResponse:
        """Call backend Risk Calculation API and enrich response for React UI."""
        payload = {
            "asset_id": req.asset_id,
            "tenant_id": req.tenant_id,
            "ahs": {
                "age_years": req.age_years,
                "material": req.material,
                "remaining_fiber_pct": req.remaining_fiber_pct,
                "defect_severity": req.defect_severity,
                "lean_deg": req.lean_deg,
                "attachment_count": req.attachment_count,
                "asset_class": req.asset_class,
                "reinforced_within_10_years": req.reinforced_within_10_years,
            },
            "consequence": {
                "population_exposure": req.population_exposure,
                "critical_infrastructure": req.critical_infrastructure,
                "service_impact": req.service_impact,
            },
            "cqs": {
                "failure_cost": req.failure_cost,
                "outage_duration_hours": req.outage_duration_hours,
                "customer_count": req.customer_count,
            },
            "weather": {
                "wind_speed_mph": req.wind_speed_mph,
                "temperature_f": req.temperature_f,
                "relative_humidity_pct": req.relative_humidity_pct,
                "precipitation_in": req.precipitation_in,
                "fire_weather_index": req.fire_weather_index,
            },
            "days_overdue": req.days_overdue,
            "work_already_scheduled": req.work_already_scheduled,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{self.backend_url}/api/v1/risks/calculate", json=payload)
            resp.raise_for_status()
            data = resp.json()

        score = data.get("risk_score", 0.0)
        category = data.get("risk_category", "UNKNOWN")

        # Color mapping & action recommendation
        color_map = {
            "CRITICAL": "#ef4444",
            "VERY_HIGH": "#f97316",
            "HIGH": "#eab308",
            "MODERATE": "#3b82f6",
            "LOW": "#10b981",
        }
        color = color_map.get(category.upper(), "#6b7280")

        if category in ("CRITICAL", "VERY_HIGH"):
            rec = "Immediate field dispatch and structural reinforcement required."
        elif category == "HIGH":
            rec = "Schedule maintenance work within 30 days. Priority queue escalated."
        elif category == "MODERATE":
            rec = "Monitor during next routine cycle. Routine inspection recommended."
        else:
            rec = "Asset operating within normal safety limits. No immediate action."

        factor_scores = {
            "AHS": data.get("ahs", 0.0),
            "CES": data.get("ces", 0.0),
            "CQS": data.get("cqs", 0.0),
            "DHM": data.get("dhm", 0.0),
            "OPS": data.get("ops", 0.0),
            "VES": data.get("ves", 0.0),
        }

        return BffEnrichedRiskResponse(
            risk_evaluation_id=data.get("risk_evaluation_id", ""),
            asset_id=data.get("asset_id", req.asset_id),
            tenant_id=data.get("tenant_id", req.tenant_id),
            risk_score=score,
            risk_category=category,
            category_color=color,
            action_recommendation=rec,
            confidence=data.get("confidence", 1.0),
            calculated_at=data.get("calculated_at", ""),
            factor_scores=factor_scores,
            drivers=data.get("explanation", {}).get("factors", []),
            warnings=data.get("warnings", []),
        )

    async def evaluate_financials(self, req: BffFinancialEngineRequest) -> BffEnrichedFinancialResponse:
        """Call backend Financial Engine API and format results."""
        payload = {
            "asset_id": req.asset_id,
            "tenant_id": req.tenant_id,
            "condition_band": req.condition_band,
            "replacement_cost": req.replacement_cost,
            "customers": req.customers,
            "outage_hours": req.outage_hours,
            "outage_cost_per_customer_hour": req.outage_cost_per_customer_hour,
            "wildfire_liability_exposure": req.wildfire_liability_exposure,
            "hftd_tier": req.hftd_tier,
            "action_cost": req.action_cost,
            "remaining_life": req.remaining_life,
            "design_life": req.design_life,
            "discount_rate": req.discount_rate,
            "degradation_rate": req.degradation_rate,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{self.backend_url}/api/v1/financial-engine/evaluate", json=payload)
            resp.raise_for_status()
            data = resp.json()

        base_summary = data.get("base_summary", {})
        net_benefit = base_summary.get("net_benefit", 0.0)
        roi = base_summary.get("roi", 0.0)
        eal = base_summary.get("eal", 0.0)

        fmt_net_benefit = f"${net_benefit:,.2f}"
        fmt_roi = f"{roi * 100:.1f}%"
        fmt_eal = f"${eal:,.2f}"

        if roi > 2.0:
            invest_rec = "Strong positive return on investment. Immediate capital allocation justified."
        elif roi > 0.0:
            invest_rec = "Favorable net benefit. Recommended for upcoming budget allocation."
        else:
            invest_rec = "Negative net benefit. Defer major overhaul unless required by risk threshold."

        return BffEnrichedFinancialResponse(
            evaluation_id=data.get("evaluation_id", ""),
            asset_id=data.get("asset_id", req.asset_id),
            tenant_id=data.get("tenant_id", req.tenant_id),
            calculation_version=data.get("calculation_version", "1.0"),
            scenarios=data.get("scenarios", {}),
            base_summary=base_summary,
            investment_recommendation=invest_rec,
            formatted_net_benefit=fmt_net_benefit,
            formatted_roi=fmt_roi,
            formatted_eal=fmt_eal,
        )

    async def calculate_pole_priority(self, req: BffPolePriorityRequest) -> BffEnrichedPriorityResponse:
        """Call backend Pole Priority API and compute work queue tier."""
        payload = {
            "asset_id": req.asset_id,
            "tenant_id": req.tenant_id,
            "composite_risk_score": req.composite_risk_score,
            "consequence_score": req.consequence_score,
            "hazard_exposure_score": req.hazard_exposure_score,
            "days_overdue": req.days_overdue,
            "inspection_confidence": req.inspection_confidence,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{self.backend_url}/api/v1/risks/pole-priority", json=payload)
            resp.raise_for_status()
            data = resp.json()

        priority_score = data.get("priority_score", 0.0)
        if priority_score >= 80.0:
            tier = "P1 - EMERGENCY / IMMEDIATE"
            color = "#ef4444"
            urgency = "Dispatch field crew immediately. High public safety risk."
        elif priority_score >= 60.0:
            tier = "P2 - HIGH URGENCY"
            color = "#f97316"
            urgency = "Queue for work order authorization within 7 days."
        elif priority_score >= 40.0:
            tier = "P3 - MEDIUM PRIORITY"
            color = "#eab308"
            urgency = "Schedule replacement in current quarterly plan."
        else:
            tier = "P4 - ROUTINE / DEFERRABLE"
            color = "#10b981"
            urgency = "No work order required at present."

        return BffEnrichedPriorityResponse(
            asset_id=req.asset_id,
            tenant_id=req.tenant_id,
            priority_score=priority_score,
            priority_tier=tier,
            priority_color=color,
            urgency_recommendation=urgency,
            score_breakdown=data.get("breakdown", {}),
        )

    async def run_unified_audit(self, asset_id: str, tenant_id: str) -> BffUnifiedAuditResponse:
        """Orchestrate risk, financial evaluation, priority, and history into a single payload."""
        risk_req = BffRiskCalculationRequest(asset_id=asset_id, tenant_id=tenant_id)
        fin_req = BffFinancialEngineRequest(asset_id=asset_id, tenant_id=tenant_id)

        risk_res = await self.calculate_risk(risk_req)
        fin_res = await self.evaluate_financials(fin_req)

        prio_req = BffPolePriorityRequest(
            asset_id=asset_id,
            tenant_id=tenant_id,
            composite_risk_score=risk_res.risk_score,
            consequence_score=risk_res.factor_scores.get("CES", 50.0),
            hazard_exposure_score=risk_res.factor_scores.get("DHM", 50.0),
        )
        prio_res = await self.calculate_pole_priority(prio_req)

        history_count = 0
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                hist_resp = await client.get(f"{self.backend_url}/api/v1/risks/history/{asset_id}?tenant_id={tenant_id}")
                if hist_resp.status_code == 200:
                    history_count = len(hist_resp.json())
            except Exception as e:
                logger.warning(f"Could not fetch history for asset {asset_id}: {e}")

        health_status = "STABLE"
        if risk_res.risk_category in ("CRITICAL", "VERY_HIGH") or prio_res.priority_score >= 80:
            health_status = "CRITICAL ACTION REQUIRED"
        elif risk_res.risk_category == "HIGH":
            health_status = "ELEVATED RISK"

        from datetime import datetime, timezone
        return BffUnifiedAuditResponse(
            asset_id=asset_id,
            tenant_id=tenant_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            risk=risk_res,
            financials=fin_res,
            priority=prio_res,
            history_count=history_count,
            overall_health_status=health_status,
        )
