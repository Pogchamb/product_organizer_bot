from abc import ABC, abstractmethod
from uuid import UUID

from trip_master.domain.entities.trip import Trip


class TripRepository(ABC):
    @abstractmethod
    async def get_by_id(self, trip_id: UUID) -> Trip | None:
        ...

    @abstractmethod
    async def get_by_chat_id(self, chat_id: int) -> list[Trip]:
        ...

    @abstractmethod
    async def get_active_by_chat_id(self, chat_id: int) -> Trip | None:
        ...

    @abstractmethod
    async def create(self, trip: Trip) -> Trip:
        ...

    @abstractmethod
    async def update(self, trip: Trip) -> Trip:
        ...
