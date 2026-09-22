from collections import defaultdict

from app.domain.schemas.financial_engine import FinancialEngineResult
from app.infrastructure.persistence.database import session_scope
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.repositories import FinancialEvaluationRepository


class FinancialHistoryRepository:
    """Append-only ROI evaluation history with a latest-result projection."""

    def __init__(self) -> None:
        self._history: dict[tuple[str, str], list[FinancialEngineResult]] = defaultdict(list)

    def append(self, result: FinancialEngineResult) -> FinancialEngineResult:
        key = (result.tenant_id, result.asset_id)
        self._history[key].append(result)
        return result

    def history(self, tenant_id: str, asset_id: str) -> list[FinancialEngineResult]:
        return list(self._history.get((tenant_id, asset_id), []))

    def latest(self, tenant_id: str, asset_id: str) -> FinancialEngineResult | None:
        records = self._history.get((tenant_id, asset_id), [])
        return records[-1] if records else None


class SqlFinancialHistoryRepository:
    """Durable append-only financial evaluation history adapter."""

    def __init__(self, engine, session_factory) -> None:
        self.session_factory = session_factory
        Base.metadata.create_all(engine)

    def append(self, result: FinancialEngineResult) -> FinancialEngineResult:
        with session_scope(self.session_factory) as session:
            FinancialEvaluationRepository(session, result.tenant_id).save(result)
        return result

    def history(self, tenant_id: str, asset_id: str) -> list[FinancialEngineResult]:
        with session_scope(self.session_factory) as session:
            rows = FinancialEvaluationRepository(session, tenant_id).history(asset_id)
            return [_to_result(row) for row in rows]

    def latest(self, tenant_id: str, asset_id: str) -> FinancialEngineResult | None:
        with session_scope(self.session_factory) as session:
            row = FinancialEvaluationRepository(session, tenant_id).latest(asset_id)
            return _to_result(row) if row else None


def _to_result(row) -> FinancialEngineResult:
    scenarios = row.scenarios
    return FinancialEngineResult.model_validate(
        {
            "roi_evaluation_id": row.id,
            "tenant_id": row.tenant_id,
            "asset_id": row.asset_id,
            "risk_evaluation_id": row.risk_evaluation_id,
            "assumption_version": row.assumption_version,
            "calculation_version": row.calculation_version,
            "currency": row.currency,
            "status": row.status,
            "scenarios": scenarios,
            "inputs_snapshot": row.inputs_snapshot,
        }
    )
