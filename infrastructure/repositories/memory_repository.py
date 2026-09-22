from typing import Generic, TypeVar

T = TypeVar("T")


class TenantMemoryRepository(Generic[T]):
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], T] = {}

    def save(self, tenant_id: str, item_id: str, item: T) -> T:
        self._items[(tenant_id, item_id)] = item
        return item

    def get(self, tenant_id: str, item_id: str) -> T | None:
        return self._items.get((tenant_id, item_id))

    def list(self, tenant_id: str) -> list[T]:
        return [item for (item_tenant, _), item in self._items.items() if item_tenant == tenant_id]
