from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trip_master.domain.entities.trip import Trip
from trip_master.domain.enums import TripStatus
from trip_master.domain.interfaces.trip_repo import TripRepository
from trip_master.infrastructure.db.models import TripModel


class SqlAlchemyTripRepository(TripRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, trip_id: UUID) -> Trip | None:
        result = await self._session.get(TripModel, str(trip_id))
        return self._to_domain(result) if result else None

    async def get_by_chat_id(self, chat_id: int) -> list[Trip]:
        result = await self._session.execute(
            select(TripModel).where(TripModel.chat_id == chat_id).order_by(TripModel.created_at.desc())
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def get_active_by_chat_id(self, chat_id: int) -> Trip | None:
        result = await self._session.execute(
            select(TripModel)
            .where(
                TripModel.chat_id == chat_id, TripModel.status == TripStatus.active
            )
            .order_by(TripModel.created_at.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return self._to_domain(row) if row else None

    async def create(self, trip: Trip) -> Trip:
        model = self._to_model(trip)
        self._session.add(model)
        await self._session.commit()
        return trip

    async def update(self, trip: Trip) -> Trip:
        model = await self._session.get(TripModel, str(trip.id))
        if model:
            model.name = trip.name
            model.status = trip.status.value
            await self._session.commit()
        return trip

    def _to_domain(self, model: TripModel) -> Trip:
        return Trip(
            id=UUID(model.id),
            chat_id=model.chat_id,
            name=model.name,
            status=TripStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Trip) -> TripModel:
        return TripModel(
            id=str(entity.id),
            chat_id=entity.chat_id,
            name=entity.name,
            status=entity.status.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
