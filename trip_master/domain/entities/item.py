from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from trip_master.domain.enums import Category


@dataclass
class Item:
    id: UUID
    trip_id: UUID
    name: str
    category: Category
    amount: str
    is_bought: bool
    buyer_id: int | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        trip_id: UUID,
        name: str,
        category: Category,
        amount: str = "",
        buyer_id: int | None = None,
    ) -> "Item":
        now = datetime.utcnow()
        return Item(
            id=uuid4(),
            trip_id=trip_id,
            name=name,
            category=category,
            amount=amount,
            is_bought=False,
            buyer_id=buyer_id,
            created_at=now,
            updated_at=now,
        )
