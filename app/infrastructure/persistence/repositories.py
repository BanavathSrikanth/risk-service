from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime
from typing import Generic, TypeVar

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.domain.schemas.financial_engine import FinancialEngineResult
from app.domain.schemas.risk_result import RiskResult

from .models import (
    FinancialEvaluation,
    IngestionRecord,
    RiskEvaluation,
    RiskEvaluationHistory,
    SourceRegistry,
    VegetationCondition,
    VegetationExposure,
    TenantRecord,
)

T = TypeVar("T")


class TenantRepository(Generic[T]):
    """Small repository base that makes tenant scoping explicit and mandatory."""

    def __init__(self, session: Session, tenant_id: str):
        if not tenant_id:
            raise ValueError("tenant_id is required")
        self.session = session
        self.tenant_id = tenant_id

    def _tenant(self, statement: Select):
        return statement.where(self.model.tenant_id == self.tenant_id)


class TenantRecordRepository:
    model = TenantRecord

    def __init__(self, session: Session, tenant_id: str, entity_type: str):
        if not tenant_id or not entity_type:
            raise ValueError("tenant_id and entity_type are required")
        self.session = session
        self.tenant_id = tenant_id
        self.entity_type = entity_type

    def save(self, entity_id: str, payload: dict) -> dict:
        row = self.session.scalar(
            select(TenantRecord).where(
                TenantRecord.tenant_id == self.tenant_id,
                TenantRecord.entity_type == self.entity_type,
                TenantRecord.entity_id == entity_id,
            )
        )
        if row is None:
            row = TenantRecord(
                tenant_id=self.tenant_id,
                entity_type=self.entity_type,
                entity_id=entity_id,
                payload=payload,
            )
            self.session.add(row)
        else:
            row.payload = payload
        self.session.flush()
        return row.payload

    def get(self, entity_id: str) -> dict | None:
        row = self.session.scalar(
            select(TenantRecord).where(
                TenantRecord.tenant_id == self.tenant_id,
                TenantRecord.entity_type == self.entity_type,
                TenantRecord.entity_id == entity_id,
            )
        )
        return row.payload if row else None

    def list(self) -> list[dict]:
        return list(
            self.session.scalars(
                select(TenantRecord).where(
                    TenantRecord.tenant_id == self.tenant_id,
                    TenantRecord.entity_type == self.entity_type,
                )
            ).all()
        )


class RiskEvaluationRepository(TenantRepository[RiskEvaluation]):
    model = RiskEvaluation

    def save(self, result: RiskResult) -> RiskEvaluation:
        if result.tenant_id != self.tenant_id:
            raise ValueError("result tenant_id does not match repository tenant")
        current = self.session.scalar(
            self._tenant(
                select(RiskEvaluation).where(RiskEvaluation.asset_id == result.asset_id)
            )
        )
        values = {
            "tenant_id": self.tenant_id,
            "asset_id": result.asset_id,
            "risk_score": result.risk_score,
            "risk_category": result.risk_category,
            "factor_scores": {
                "ahs": result.ahs, "ces": result.ces, "cqs": result.cqs,
                "dhm": result.dhm, "ops": result.ops, "ves": result.ves,
            },
            "input_values": result.input_values,
            "explanation": result.explanation,
            "source_captured_at": result.source_captured_at,
            "source_event_id": result.source_event_id,
            "calculation_version": result.calculation_version,
            "confidence": result.confidence,
            "calculated_at": result.calculated_at,
        }
        if current is None:
            current = RiskEvaluation(**values)
            self.session.add(current)
        else:
            for key, value in values.items():
                setattr(current, key, value)
        self.session.flush()
        self.session.add(RiskEvaluationHistory(risk_evaluation_id=current.id, **values))
        self.session.flush()
        return current

    def latest(self, asset_id: str) -> RiskEvaluation | None:
        return self.session.scalar(
            self._tenant(select(RiskEvaluation).where(RiskEvaluation.asset_id == asset_id))
        )

    def history(self, asset_id: str) -> Sequence[RiskEvaluationHistory]:
        return self.session.scalars(
            select(RiskEvaluationHistory)
            .where(
                RiskEvaluationHistory.tenant_id == self.tenant_id,
                RiskEvaluationHistory.asset_id == asset_id,
            )
            .order_by(RiskEvaluationHistory.calculated_at.asc())
        ).all()


class FinancialEvaluationRepository(TenantRepository[FinancialEvaluation]):
    model = FinancialEvaluation

    def save(self, result: FinancialEngineResult) -> FinancialEvaluation:
        if result.tenant_id != self.tenant_id:
            raise ValueError("result tenant_id does not match repository tenant")
        row = FinancialEvaluation(
            id=result.roi_evaluation_id,
            tenant_id=self.tenant_id,
            asset_id=result.asset_id,
            risk_evaluation_id=result.risk_evaluation_id,
            assumption_version=result.assumption_version,
            calculation_version=result.calculation_version,
            currency=result.currency,
            status=result.status,
            scenarios=[scenario.model_dump(mode="json") for scenario in result.scenarios],
            inputs_snapshot=result.inputs_snapshot,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def history(self, asset_id: str) -> Sequence[FinancialEvaluation]:
        return self.session.scalars(
            self._tenant(
                select(FinancialEvaluation)
                .where(FinancialEvaluation.asset_id == asset_id)
                .order_by(FinancialEvaluation.created_at.asc())
            )
        ).all()

    def latest(self, asset_id: str) -> FinancialEvaluation | None:
        return self.session.scalar(
            self._tenant(
                select(FinancialEvaluation)
                .where(FinancialEvaluation.asset_id == asset_id)
                .order_by(FinancialEvaluation.created_at.desc())
                .limit(1)
            )
        )


class SourceRegistryRepository(TenantRepository[SourceRegistry]):
    model = SourceRegistry

    def upsert(self, **values) -> SourceRegistry:
        source = self.session.scalar(
            self._tenant(
                select(SourceRegistry).where(SourceRegistry.source_key == values["source_key"])
            )
        )
        values["tenant_id"] = self.tenant_id
        if source is None:
            source = SourceRegistry(**values)
            self.session.add(source)
        else:
            for key, value in values.items():
                if key != "tenant_id":
                    setattr(source, key, value)
        self.session.flush()
        return source

    def get(self, source_key: str) -> SourceRegistry | None:
        return self.session.scalar(
            self._tenant(select(SourceRegistry).where(SourceRegistry.source_key == source_key))
        )

    def list(self) -> Sequence[SourceRegistry]:
        return self.session.scalars(
            self._tenant(select(SourceRegistry).order_by(SourceRegistry.name))
        ).all()


class IngestionRecordRepository(TenantRepository[IngestionRecord]):
    model = IngestionRecord

    def add(self, **values) -> IngestionRecord:
        row = IngestionRecord(tenant_id=self.tenant_id, **values)
        self.session.add(row)
        self.session.flush()
        return row

    def get(self, record_id: str) -> IngestionRecord | None:
        return self.session.scalar(
            self._tenant(select(IngestionRecord).where(IngestionRecord.id == record_id))
        )


class VegetationRepository(TenantRepository[T]):
    model = VegetationCondition

    def conditions(self, asset_id: str, *, since: datetime | None = None):
        statement = select(VegetationCondition).where(
            VegetationCondition.asset_id == asset_id
        )
        if since is not None:
            statement = statement.where(VegetationCondition.observed_at >= since)
        return self.session.scalars(
            self._tenant(statement.order_by(VegetationCondition.observed_at.desc()))
        ).all()

    def exposures(self, asset_id: str, *, since: datetime | None = None):
        statement = select(VegetationExposure).where(
            VegetationExposure.asset_id == asset_id
        )
        if since is not None:
            statement = statement.where(VegetationExposure.observed_at >= since)
        return self.session.scalars(
            self._tenant(statement.order_by(VegetationExposure.observed_at.desc()))
        ).all()

    def add_condition(self, **values) -> VegetationCondition:
        row = VegetationCondition(tenant_id=self.tenant_id, **values)
        self.session.add(row)
        self.session.flush()
        return row

    def add_exposure(self, **values) -> VegetationExposure:
        row = VegetationExposure(tenant_id=self.tenant_id, **values)
        self.session.add(row)
        self.session.flush()
        return row
