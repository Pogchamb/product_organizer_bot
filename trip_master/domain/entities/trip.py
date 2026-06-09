from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from trip_master.domain.enums import TripStatus


@dataclass
class Trip:
    id: UUID
    chat_id: int
    name: str
    status: TripStatus
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(chat_id: int, name: str) -> "Trip":
        now = datetime.now(UTC)
        return Trip(
            id=uuid4(),
            chat_id=chat_id,
            name=name,
            status=TripStatus.active,
            created_at=now,
            updated_at=now,
        )
