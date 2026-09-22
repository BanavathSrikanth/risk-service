from copy import deepcopy
from typing import Any

from app.domain.schemas.risk_result import RiskResult
from app.infrastructure.persistence.database import session_scope
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.repositories import RiskEvaluationRepository


class RiskHistoryRepository:
    """Append-only risk evaluation history with a latest-result projection."""

    def __init__(self) -> None:
        self._history: list[RiskResult] = []
        self._latest: dict[tuple[str, str], RiskResult] = {}

    def append(self, result: RiskResult) -> RiskResult:
        snapshot = deepcopy(result)
        self._history.append(snapshot)
        self._latest[(snapshot.tenant_id, snapshot.asset_id)] = snapshot
        return deepcopy(snapshot)

    def latest(self, tenant_id: str, asset_id: str) -> RiskResult | None:
        result = self._latest.get((tenant_id, asset_id))
        return deepcopy(result) if result else None

    def history(self, tenant_id: str, asset_id: str) -> list[RiskResult]:
        return [
            deepcopy(result)
            for result in self._history
            if result.tenant_id == tenant_id and result.asset_id == asset_id
        ]


class SqlRiskHistoryRepository:
    """Durable risk history adapter backed by the immutable history table."""

    def __init__(self, engine: Any, session_factory: Any) -> None:
        self.engine = engine
        self.session_factory = session_factory
        Base.metadata.create_all(engine)

    def append(self, result: RiskResult) -> RiskResult:
        with session_scope(self.session_factory) as session:
            RiskEvaluationRepository(session, result.tenant_id).save(result)
        return result

    def latest(self, tenant_id: str, asset_id: str) -> RiskResult | None:
        with session_scope(self.session_factory) as session:
            row = RiskEvaluationRepository(session, tenant_id).latest(asset_id)
            if row is None:
                return None
            return _to_risk_result(row)

    def history(self, tenant_id: str, asset_id: str) -> list[RiskResult]:
        with session_scope(self.session_factory) as session:
            rows = RiskEvaluationRepository(session, tenant_id).history(asset_id)
            return [_history_to_risk_result(row) for row in rows]


def _result_values(row: Any) -> dict[str, Any]:
    factors = row.factor_scores
    return {
        "risk_evaluation_id": row.id,
        "asset_id": row.asset_id,
        "tenant_id": row.tenant_id,
        "risk_score": float(row.risk_score),
        "risk_category": row.risk_category,
        "ahs": float(factors.get("ahs", 0)),
        "ces": float(factors.get("ces", 0)),
        "cqs": float(factors.get("cqs", 0)),
        "dhm": float(factors.get("dhm", 0)),
        "ops": float(factors.get("ops", 0)),
        "ves": float(factors.get("ves", 0)),
        "calculated_at": row.calculated_at,
        "source_captured_at": row.source_captured_at,
        "source_event_id": row.source_event_id,
        "calculation_version": row.calculation_version,
        "input_values": row.input_values,
        "explanation": row.explanation,
        "confidence": float(row.confidence),
    }


def _to_risk_result(row: Any) -> RiskResult:
    return RiskResult.model_validate(_result_values(row))


def _history_to_risk_result(row: Any) -> RiskResult:
    return RiskResult.model_validate(_result_values(row))
