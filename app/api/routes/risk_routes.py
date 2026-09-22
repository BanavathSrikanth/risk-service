from fastapi import APIRouter, Depends, HTTPException

from app.application.services.risk_calculation_service import RiskCalculationService
from app.infrastructure.repositories.risk_repository import RiskRepository

router = APIRouter(prefix="/risks", tags=["risks"])


def get_risk_service() -> RiskCalculationService:
    return RiskCalculationService(RiskRepository())


@router.post("/calculate")
async def calculate_risk(
    payload: dict,
    service: RiskCalculationService = Depends(get_risk_service),
):
    try:
        result = service.calculate(
            asset_id=payload["asset_id"],
            tenant_id=payload["tenant_id"],
            ahs=float(payload["ahs"]),
            ces=float(payload["ces"]),
            cqs=float(payload["cqs"]),
            dhm=float(payload["dhm"]),
            ops=float(payload["ops"]),
            ves=float(payload.get("ves", 0.0)),
        )
        return {
            "risk_evaluation_id": result.risk_evaluation_id,
            "asset_id": result.asset_id,
            "tenant_id": result.tenant_id,
            "risk_score": result.risk_score,
            "ves": result.ves,
            "risk_category": result.risk_category,
            "calculated_at": result.calculated_at.isoformat(),
            "drivers": result.drivers,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.get("/latest/{asset_id}")
async def get_latest_risk(
    asset_id: str,
    tenant_id: str,
    service: RiskCalculationService = Depends(get_risk_service),
):
    result = service.repository.get_latest(tenant_id, asset_id)
    if result is None:
        raise HTTPException(status_code=404, detail="No risk result found")
    return {
        "risk_evaluation_id": result.risk_evaluation_id,
        "asset_id": result.asset_id,
        "tenant_id": result.tenant_id,
        "risk_score": result.risk_score,
        "ves": result.ves,
        "risk_category": result.risk_category,
        "calculated_at": result.calculated_at.isoformat(),
        "drivers": result.drivers,
    }
