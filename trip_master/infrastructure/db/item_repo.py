from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from trip_master.domain.entities.item import Item
from trip_master.domain.enums import Category
from trip_master.domain.interfaces.item_repo import ItemRepository
from trip_master.infrastructure.db.models import ItemModel


class SqlAlchemyItemRepository(ItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, item_id: UUID) -> Item | None:
        model = await self._session.get(ItemModel, str(item_id))
        return self._to_domain(model) if model else None

    async def get_by_trip(self, trip_id: UUID) -> list[Item]:
        result = await self._session.execute(
            select(ItemModel)
            .where(ItemModel.trip_id == str(trip_id))
            .order_by(ItemModel.created_at.asc())
        )
        return [self._to_domain(row) for row in result.scalars().all()]

    async def create(self, item: Item) -> Item:
        model = self._to_model(item)
        self._session.add(model)
        await self._session.commit()
        return item

    async def create_many(self, items: list[Item]) -> list[Item]:
        models = [self._to_model(item) for item in items]
        self._session.add_all(models)
        await self._session.commit()
        return items

    async def update(self, item: Item) -> Item:
        model = await self._session.get(ItemModel, str(item.id))
        if model:
            model.name = item.name
            model.category = item.category.value
            model.amount = item.amount
            model.is_bought = item.is_bought
            model.buyer_id = item.buyer_id
            await self._session.commit()
        return item

    async def delete(self, item_id: UUID) -> None:
        model = await self._session.get(ItemModel, str(item_id))
        if model:
            await self._session.delete(model)
            await self._session.commit()

    def _to_domain(self, model: ItemModel) -> Item:
        return Item(
            id=UUID(model.id),
            trip_id=UUID(model.trip_id),
            name=model.name,
            category=Category(model.category),
            amount=model.amount,
            is_bought=model.is_bought,
            buyer_id=model.buyer_id,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_model(self, entity: Item) -> ItemModel:
        return ItemModel(
            id=str(entity.id),
            trip_id=str(entity.trip_id),
            name=entity.name,
            category=entity.category.value,
            amount=entity.amount,
            is_bought=entity.is_bought,
            buyer_id=entity.buyer_id,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
