from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TenantRequest(BaseModel):
    tenant_id: str = Field(min_length=1)


class AssetCreate(TenantRequest):
    asset_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    asset_class: str = Field(min_length=1)
    material: str | None = None
    status: Literal["active", "inactive", "retired"] = "active"
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Asset(AssetCreate):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InspectionCreate(TenantRequest):
    asset_id: str = Field(min_length=1)
    inspector_id: str = Field(min_length=1)
    inspected_at: datetime
    condition_score: float = Field(ge=0, le=100)
    defect_severity: Literal["none", "minor", "moderate", "major", "critical"]
    exposure_level: float = Field(default=0, ge=0, le=100)
    evidence_count: int = Field(default=0, ge=0)
    notes: str | None = None
    evidence_blob_name: str | None = None


class Inspection(InspectionCreate):
    inspection_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FinancialCreate(TenantRequest):
    asset_id: str = Field(min_length=1)
    currency: str = Field(min_length=3, max_length=3)
    replacement_cost: float = Field(ge=0)
    annual_operating_cost: float = Field(default=0, ge=0)
    outage_cost_per_hour: float = Field(default=0, ge=0)
    customer_count: int = Field(default=0, ge=0)
    effective_from: datetime


class Financial(FinancialCreate):
    financial_id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class GeoUpdate(TenantRequest):
    asset_id: str = Field(min_length=1)
    point: GeoPoint
    source: Literal["manual", "osm", "import"] = "manual"


class MapConfig(BaseModel):
    provider: str = "osm"
    style_url: str
    tile_url: str
    attribution: str = "© OpenStreetMap contributors"


class RiskCalculationRequest(TenantRequest):
    asset_id: str = Field(min_length=1)
    risk_input: dict[str, Any]
