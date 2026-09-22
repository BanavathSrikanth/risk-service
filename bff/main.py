import os
import httpx
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from bff.models import (
    BffRiskCalculationRequest,
    BffFinancialEngineRequest,
    BffPolePriorityRequest,
    BffUnifiedAuditRequest,
    BffEnrichedRiskResponse,
    BffEnrichedFinancialResponse,
    BffEnrichedPriorityResponse,
    BffUnifiedAuditResponse,
)
from bff.bff_service import BffService, BACKEND_SERVICE_URL

app = FastAPI(
    title="InfraIQ Risk Service - BFF (Backend-For-Frontend)",
    version="1.0.0",
    description="Dedicated BFF service providing aggregated, UI-optimized endpoints for the React frontend.",
)

# Enable CORS for React Frontend (running on port 3000 / 5173 / localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

bff_service = BffService(BACKEND_SERVICE_URL)


@app.get("/bff/health", tags=["BFF Health"])
async def bff_health():
    """Health check for BFF service and downstream risk backend connection."""
    backend_status = "unreachable"
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            res = await client.get(f"{BACKEND_SERVICE_URL}/health")
            if res.status_code == 200:
                backend_status = "healthy"
    except Exception:
        backend_status = "error"

    return {
        "status": "healthy",
        "service": "bff-service",
        "port": 8001,
        "backend_url": BACKEND_SERVICE_URL,
        "backend_status": backend_status,
    }


@app.post(
    "/bff/api/v1/calculate-risk",
    response_model=BffEnrichedRiskResponse,
    tags=["BFF Risk API"],
    summary="Frontend button endpoint for calculating risk",
)
async def calculate_risk(request: BffRiskCalculationRequest):
    try:
        return await bff_service.calculate_risk(request)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Backend Risk Service error: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BFF internal error: {str(exc)}",
        )


@app.post(
    "/bff/api/v1/evaluate-financials",
    response_model=BffEnrichedFinancialResponse,
    tags=["BFF Financial API"],
    summary="Frontend button endpoint for financial engine evaluation",
)
async def evaluate_financials(request: BffFinancialEngineRequest):
    try:
        return await bff_service.evaluate_financials(request)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Backend Financial Engine error: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BFF internal error: {str(exc)}",
        )


@app.post(
    "/bff/api/v1/pole-priority",
    response_model=BffEnrichedPriorityResponse,
    tags=["BFF Pole Priority API"],
    summary="Frontend button endpoint for pole work priority",
)
async def pole_priority(request: BffPolePriorityRequest):
    try:
        return await bff_service.calculate_pole_priority(request)
    except httpx.HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Backend Pole Priority error: {exc.response.text}",
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"BFF internal error: {str(exc)}",
        )


@app.post(
    "/bff/api/v1/asset-risk-summary",
    response_model=BffUnifiedAuditResponse,
    tags=["BFF Unified Audit API"],
    summary="Single-click comprehensive asset audit button",
)
async def asset_risk_summary(request: BffUnifiedAuditRequest):
    try:
        return await bff_service.run_unified_audit(
            asset_id=request.asset_id, tenant_id=request.tenant_id
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate unified audit: {str(exc)}",
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
