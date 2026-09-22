from abc import ABC, abstractmethod

from app.domain.schemas.risk_result import RiskResult


class RiskRepository(ABC):

    @abstractmethod
    def save(self, result: RiskResult) -> None:
        """Persist a risk result."""
        raise NotImplementedError

    @abstractmethod
    def get_by_asset(
        self,
        tenant_id: str,
        asset_id: str,
    ) -> list[RiskResult]:
        """Return risk history for an asset."""
        raise NotImplementedError


class InMemoryRiskRepository(RiskRepository):

    def __init__(self) -> None:
        self._results: list[RiskResult] = []

    def save(self, result: RiskResult) -> None:
        self._results.append(result)

    def get_by_asset(
        self,
        tenant_id: str,
        asset_id: str,
    ) -> list[RiskResult]:

        results = [
            result
            for result in self._results
            if result.tenant_id == tenant_id
            and result.asset_id == asset_id
        ]

        return sorted(
            results,
            key=lambda result: result.calculated_at,
        )