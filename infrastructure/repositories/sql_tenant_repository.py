from typing import Generic, TypeVar

from pydantic import BaseModel

from app.infrastructure.persistence.database import session_scope
from app.infrastructure.persistence.models import Base
from app.infrastructure.persistence.repositories import TenantRecordRepository

T = TypeVar("T", bound=BaseModel)


class SqlTenantRepository(Generic[T]):
    def __init__(self, engine, session_factory, entity_type: str, model: type[T]) -> None:
        self.engine = engine
        self.session_factory = session_factory
        self.entity_type = entity_type
        self.model = model
        Base.metadata.create_all(engine)

    def save(self, tenant_id: str, entity_id: str, value: T) -> T:
        with session_scope(self.session_factory) as session:
            TenantRecordRepository(session, tenant_id, self.entity_type).save(
                entity_id, value.model_dump(mode="json")
            )
        return value

    def get(self, tenant_id: str, entity_id: str) -> T | None:
        with session_scope(self.session_factory) as session:
            payload = TenantRecordRepository(
                session, tenant_id, self.entity_type
            ).get(entity_id)
        return self.model.model_validate(payload) if payload else None

    def list(self, tenant_id: str) -> list[T]:
        with session_scope(self.session_factory) as session:
            rows = TenantRecordRepository(
                session, tenant_id, self.entity_type
            ).list()
        return [self.model.model_validate(row.payload) for row in rows]
