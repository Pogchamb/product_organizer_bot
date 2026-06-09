from abc import ABC, abstractmethod
from uuid import UUID

from trip_master.domain.entities.item import Item


class ItemRepository(ABC):
    @abstractmethod
    async def get_by_id(self, item_id: UUID) -> Item | None:
        ...

    @abstractmethod
    async def get_by_trip(self, trip_id: UUID) -> list[Item]:
        ...

    @abstractmethod
    async def create(self, item: Item) -> Item:
        ...

    @abstractmethod
    async def create_many(self, items: list[Item]) -> list[Item]:
        ...

    @abstractmethod
    async def update(self, item: Item) -> Item:
        ...

    @abstractmethod
    async def delete(self, item_id: UUID) -> None:
        ...
