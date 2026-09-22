from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4


@dataclass
class RiskResult:
    risk_evaluation_id: str
    asset_id: str
    tenant_id: str
    risk_score: float
    ves: float
    risk_category: str
    calculated_at: datetime
    drivers: dict[str, float]

    @classmethod
    def create(
        cls,
        asset_id: str,
        tenant_id: str,
        risk_score: float,
        ves: float,
        risk_category: str,
        drivers: dict[str, float],
    ) -> "RiskResult":
        return cls(
            risk_evaluation_id=str(uuid4()),
            asset_id=asset_id,
            tenant_id=tenant_id,
            risk_score=risk_score,
            ves=ves,
            risk_category=risk_category,
            calculated_at=datetime.now(timezone.utc),
            drivers=drivers,
        )
