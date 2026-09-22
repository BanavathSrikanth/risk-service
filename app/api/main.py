from pathlib import Path
from typing import Any, cast

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from libs.common.observability import CorrelationIdMiddleware

from app.application.risk_calculation import RiskCalculationService
from app.application.financial_engine import FinancialEngine
from app.config import get_settings
from app.domain.schemas.risk_input import RiskInput
from app.domain.schemas.financial_engine import (
    FinancialEngineInput,
    FinancialEngineResult,
)
from app.domain.schemas.priority import PolePriorityInput
from app.application.pole_prioritization import PolePriorityService
from app.domain.schemas.service_models import (
    Asset,
    AssetCreate,
    Financial,
    FinancialCreate,
    GeoUpdate,
    Inspection,
    InspectionCreate,
    MapConfig,
)
from infrastructure.blob_storage import BlobStorage
from infrastructure.redis_cache import RedisCache
from infrastructure.repositories.risk_history_repository import SqlRiskHistoryRepository
from infrastructure.repositories.financial_history_repository import (
    SqlFinancialHistoryRepository,
)
from app.infrastructure.persistence.database import create_engine, create_session_factory
from infrastructure.repositories.sql_tenant_repository import SqlTenantRepository

settings = get_settings()
app = FastAPI(
    title="InfraIQ Asset Intelligence API",
    version="1.0.0",
    description="Tenant-aware asset, inspection, financial, GIS, and risk APIs.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(CorrelationIdMiddleware)

risk_service = RiskCalculationService(settings.rules_directory)
financial_engine = FinancialEngine()
risk_priority_service = PolePriorityService()
database_engine = create_engine(settings.database_url)
database_session_factory = create_session_factory(database_engine)
asset_repository = SqlTenantRepository(
    database_engine, database_session_factory, "asset", Asset
)
inspection_repository = SqlTenantRepository(
    database_engine, database_session_factory, "inspection", Inspection
)
financial_repository = SqlTenantRepository(
    database_engine, database_session_factory, "financial", Financial
)
geo_repository = SqlTenantRepository(
    database_engine, database_session_factory, "geo_update", GeoUpdate
)
risk_history_repository = SqlRiskHistoryRepository(
    database_engine, database_session_factory
)
financial_history_repository = SqlFinancialHistoryRepository(
    database_engine, database_session_factory
)
blob_storage = BlobStorage(settings.blob_connection_string, settings.blob_container)
redis_cache = RedisCache(settings.redis_url)


def _tenant(value: str) -> str:
    return value.strip()


@app.get("/health", tags=["system"])
def health() -> dict[str, Any]:
    return {
        "status": "healthy",
        "service": settings.service_name,
        "environment": settings.environment,
        "integrations": {
            "redis": redis_cache.enabled,
            "blob_storage": blob_storage.enabled,
            "foundry": bool(settings.foundry_endpoint),
        },
    }


@app.post(f"{settings.api_prefix}/assets", response_model=Asset, tags=["assets"])
def create_asset(request: AssetCreate) -> Asset:
    asset = Asset.model_validate(request.model_dump())
    return asset_repository.save(_tenant(request.tenant_id), asset.asset_id, asset)


@app.get(f"{settings.api_prefix}/assets", response_model=list[Asset], tags=["assets"])
def list_assets(tenant_id: str) -> list[Asset]:
    return asset_repository.list(_tenant(tenant_id))


@app.get(f"{settings.api_prefix}/assets/{{asset_id}}", response_model=Asset, tags=["assets"])
def get_asset(asset_id: str, tenant_id: str) -> Asset:
    asset = asset_repository.get(_tenant(tenant_id), asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    return asset


@app.post(f"{settings.api_prefix}/inspections", response_model=Inspection, tags=["inspections"])
def create_inspection(request: InspectionCreate) -> Inspection:
    if not asset_repository.get(request.tenant_id, request.asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    inspection = Inspection.model_validate(request.model_dump())
    return inspection_repository.save(
        _tenant(request.tenant_id), str(inspection.inspection_id), inspection
    )


@app.get(f"{settings.api_prefix}/inspections", response_model=list[Inspection], tags=["inspections"])
def list_inspections(tenant_id: str, asset_id: str | None = None) -> list[Inspection]:
    records = inspection_repository.list(_tenant(tenant_id))
    return [record for record in records if not asset_id or record.asset_id == asset_id]


@app.post(f"{settings.api_prefix}/financials", response_model=Financial, tags=["financials"])
def create_financial(request: FinancialCreate) -> Financial:
    if not asset_repository.get(request.tenant_id, request.asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    financial = Financial.model_validate(request.model_dump())
    return financial_repository.save(
        _tenant(request.tenant_id), str(financial.financial_id), financial
    )


@app.get(f"{settings.api_prefix}/financials", response_model=list[Financial], tags=["financials"])
def list_financials(tenant_id: str, asset_id: str | None = None) -> list[Financial]:
    records = financial_repository.list(_tenant(tenant_id))
    return [record for record in records if not asset_id or record.asset_id == asset_id]


@app.put(f"{settings.api_prefix}/gis/assets/{{asset_id}}", response_model=GeoUpdate, tags=["gis"])
def update_asset_location(asset_id: str, request: GeoUpdate) -> GeoUpdate:
    if asset_id != request.asset_id:
        raise HTTPException(status_code=400, detail="Path and body asset_id must match")
    if not asset_repository.get(request.tenant_id, asset_id):
        raise HTTPException(status_code=404, detail="Asset not found")
    return geo_repository.save(_tenant(request.tenant_id), asset_id, request)


@app.get(f"{settings.api_prefix}/gis/assets/{{asset_id}}", response_model=GeoUpdate, tags=["gis"])
def get_asset_location(asset_id: str, tenant_id: str) -> GeoUpdate:
    location = geo_repository.get(_tenant(tenant_id), asset_id)
    if not location:
        raise HTTPException(status_code=404, detail="Asset location not found")
    return location


@app.get(f"{settings.api_prefix}/gis/map-config", response_model=MapConfig, tags=["gis"])
def map_config() -> MapConfig:
    return MapConfig(style_url=settings.map_style_url, tile_url=settings.osm_tile_url)


@app.get(f"{settings.api_prefix}/gis/geocode", tags=["gis"])
async def geocode(query: str) -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(
            "https://nominatim.openstreetmap.org/search",
            params={"q": query, "format": "jsonv2", "limit": 5},
            headers={"User-Agent": settings.osm_user_agent},
        )
    response.raise_for_status()
    return response.json()


@app.post(f"{settings.api_prefix}/inspections/{{inspection_id}}/evidence", tags=["inspections"])
async def upload_evidence(inspection_id: str, request: Request) -> dict[str, str]:
    if not blob_storage.enabled:
        raise HTTPException(status_code=503, detail="Blob storage is not configured")
    filename = Path(request.headers.get("x-file-name", "evidence")).name
    blob_name = f"inspections/{inspection_id}/{filename}"
    from io import BytesIO

    blob_storage.upload(
        blob_name,
        BytesIO(await request.body()),
        request.headers.get("content-type"),
    )
    return {"blob_name": blob_name}


@app.post(f"{settings.api_prefix}/risks/calculate", tags=["risks"])
def calculate_risk(request: RiskInput) -> dict[str, Any]:
    result = risk_service.calculate(request)
    result_data = result.model_dump(mode="json")
    risk_history_repository.append(result)
    redis_cache.set_json(
        f"risk:{request.tenant_id}:{request.asset_id}", result_data, ttl_seconds=300
    )
    return result_data


@app.post(
    f"{settings.api_prefix}/financial-engine/evaluate",
    response_model=FinancialEngineResult,
    tags=["financials"],
)
def evaluate_financial_engine(request: FinancialEngineInput) -> FinancialEngineResult:
    result = financial_engine.calculate(request)
    return financial_history_repository.append(result)


@app.get(
    f"{settings.api_prefix}/financial-engine/history/{{asset_id}}",
    response_model=list[FinancialEngineResult],
    tags=["financials"],
)
def financial_engine_history(
    asset_id: str, tenant_id: str
) -> list[FinancialEngineResult]:
    return financial_history_repository.history(_tenant(tenant_id), asset_id)


@app.get(f"{settings.api_prefix}/risks/latest/{{asset_id}}", tags=["risks"])
def latest_risk(asset_id: str, tenant_id: str) -> dict[str, Any]:
    result = risk_history_repository.latest(_tenant(tenant_id), asset_id)
    if result:
        return result.model_dump(mode="json")
    cached_result = redis_cache.get_json(f"risk:{_tenant(tenant_id)}:{asset_id}")
    if not cached_result:
        raise HTTPException(status_code=404, detail="No cached risk result found")
    return cast(dict[str, Any], cached_result)


@app.post(f"{settings.api_prefix}/risks/pole-priority", tags=["risks"])
def calculate_pole_priority(request: PolePriorityInput) -> dict[str, Any]:
    """Calculate a versioned queue score without authorizing or assigning work."""
    return risk_priority_service.calculate(request).model_dump(mode="json")


@app.get(f"{settings.api_prefix}/risks/history/{{asset_id}}", tags=["risks"])
def risk_history(asset_id: str, tenant_id: str) -> list[dict[str, Any]]:
    return [
        result.model_dump(mode="json")
        for result in risk_history_repository.history(_tenant(tenant_id), asset_id)
    ]
