from typing import Dict, Optional

from app.domain.entities.risk_result import RiskResult


class RiskRepository:
    def __init__(self):
        self._store: Dict[str, RiskResult] = {}
        self._history: list[RiskResult] = []

    def save(self, risk_result: RiskResult) -> RiskResult:
        key = f"{risk_result.tenant_id}:{risk_result.asset_id}"
        self._store[key] = risk_result
        self._history.append(risk_result)
        return risk_result

    def get_latest(self, tenant_id: str, asset_id: str) -> Optional[RiskResult]:
        return self._store.get(f"{tenant_id}:{asset_id}")

    def list_history(self, tenant_id: str, asset_id: str) -> list[RiskResult]:
        return [
            result
            for result in self._history
            if result.tenant_id == tenant_id and result.asset_id == asset_id
        ]
