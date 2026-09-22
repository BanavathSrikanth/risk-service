from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import uuid4

from sqlalchemy import (
    JSON,
    DateTime,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class TenantModel:
    tenant_id: Mapped[str] = mapped_column(String(128), nullable=False, index=True)


class TenantRecord(TenantModel, Base):
    """Durable transitional store for service-owned records awaiting dedicated tables."""

    __tablename__ = "tenant_records"
    __table_args__ = (
        UniqueConstraint(
            "tenant_id", "entity_type", "entity_id", name="uq_tenant_record"
        ),
        Index("ix_tenant_record_lookup", "tenant_id", "entity_type"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[str] = mapped_column(String(256), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class RiskEvaluation(TenantModel, Base):
    """Latest risk projection. Every write also creates an immutable history row."""

    __tablename__ = "risk_evaluations"
    __table_args__ = (UniqueConstraint("tenant_id", "asset_id", name="uq_risk_current"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    risk_category: Mapped[str] = mapped_column(String(64), nullable=False)
    factor_scores: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    input_values: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    explanation: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    source_captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_event_id: Mapped[str] = mapped_column(String(256), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=1)
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class RiskEvaluationHistory(TenantModel, Base):
    """Append-only audit trail; applications must never update or delete these rows."""

    __tablename__ = "risk_evaluation_history"
    __table_args__ = (
        Index("ix_risk_history_asset_time", "tenant_id", "asset_id", "calculated_at"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    risk_evaluation_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    asset_id: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_score: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    risk_category: Mapped[str] = mapped_column(String(64), nullable=False)
    factor_scores: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    input_values: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    explanation: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    source_captured_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_event_id: Mapped[str] = mapped_column(String(256), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(128), nullable=False)
    confidence: Mapped[Decimal] = mapped_column(Numeric(6, 4), nullable=False, default=1)
    calculated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class FinancialEvaluation(TenantModel, Base):
    __tablename__ = "financial_evaluations"
    __table_args__ = (Index("ix_financial_asset_time", "tenant_id", "asset_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String(128), nullable=False)
    risk_evaluation_id: Mapped[str | None] = mapped_column(String(36), index=True)
    assumption_version: Mapped[str] = mapped_column(String(128), nullable=False)
    calculation_version: Mapped[str] = mapped_column(String(128), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    scenarios: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    inputs_snapshot: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=utcnow
    )


class SourceRegistry(TenantModel, Base):
    __tablename__ = "source_registry"
    __table_args__ = (UniqueConstraint("tenant_id", "source_key", name="uq_source_key"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_key: Mapped[str] = mapped_column(String(256), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    uri: Mapped[str | None] = mapped_column(Text)
    configuration: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class IngestionRecord(TenantModel, Base):
    __tablename__ = "ingestion_records"
    __table_args__ = (Index("ix_ingestion_source_time", "tenant_id", "source_id", "started_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    source_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    external_id: Mapped[str | None] = mapped_column(String(256))
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    records_received: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    records_processed: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[str | None] = mapped_column(Text)
    metadata_json: Mapped[dict[str, Any]] = mapped_column(
        "metadata", JSON, nullable=False, default=dict
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class VegetationCondition(TenantModel, Base):
    __tablename__ = "vegetation_conditions"
    __table_args__ = (Index("ix_vegetation_asset_time", "tenant_id", "asset_id", "observed_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String(128), nullable=False)
    condition_score: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    fuel_type: Mapped[str | None] = mapped_column(String(128))
    height_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    distance_m: Mapped[Decimal | None] = mapped_column(Numeric(8, 3))
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(36))


class VegetationExposure(TenantModel, Base):
    __tablename__ = "vegetation_exposures"
    __table_args__ = (Index("ix_vegetation_exposure_asset_time", "tenant_id", "asset_id", "observed_at"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    asset_id: Mapped[str] = mapped_column(String(128), nullable=False)
    exposure_score: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    severity: Mapped[str | None] = mapped_column(String(64))
    geometry: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    attributes: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
    observed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_id: Mapped[str | None] = mapped_column(String(36))
