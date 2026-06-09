from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from trip_master.domain.entities.item import Item
from trip_master.domain.enums import Category
from trip_master.infrastructure.db.item_repo import SqlAlchemyItemRepository
from trip_master.infrastructure.db.trip_repo import SqlAlchemyTripRepository


def create_api_router(get_session):  # type: ignore[no-untyped-def]
    router = APIRouter(prefix="/api")

    @router.get("/trips")
    async def list_trips(chat_id: int, session: AsyncSession = Depends(get_session)) -> list[dict]:
        repo = SqlAlchemyTripRepository(session)
        trips = await repo.get_by_chat_id(chat_id)
        return [_trip_to_dict(t) for t in trips]

    @router.get("/trips/{trip_id}")
    async def get_trip(trip_id: UUID, session: AsyncSession = Depends(get_session)) -> dict:
        repo = SqlAlchemyTripRepository(session)
        trip = await repo.get_by_id(trip_id)
        if not trip:
            raise HTTPException(404, "Trip not found")
        return _trip_to_dict(trip)

    @router.get("/trips/{trip_id}/items")
    async def list_items(trip_id: UUID, session: AsyncSession = Depends(get_session)) -> list[dict]:
        repo = SqlAlchemyItemRepository(session)
        items = await repo.get_by_trip(trip_id)
        return [_item_to_dict(it) for it in items]

    @router.post("/trips/{trip_id}/items", status_code=201)
    async def add_item(
        trip_id: UUID,
        body: dict,
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        name = body.get("name", "").strip()
        if not name:
            raise HTTPException(400, "Name is required")
        try:
            category = Category(body.get("category", "food"))
        except ValueError:
            raise HTTPException(400, f"Invalid category: {body.get('category')}")
        amount = body.get("amount", "")

        item = Item.create(trip_id=trip_id, name=name, category=category, amount=amount)
        item_repo = SqlAlchemyItemRepository(session)
        await item_repo.create(item)
        return {"id": str(item.id)}

    @router.patch("/items/{item_id}/toggle")
    async def toggle_item(
        item_id: UUID,
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        item_repo = SqlAlchemyItemRepository(session)
        item = await item_repo.get_by_id(item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        item.is_bought = not item.is_bought
        await item_repo.update(item)
        return {"id": str(item.id), "is_bought": item.is_bought}

    @router.patch("/items/{item_id}/buyer")
    async def set_buyer(
        item_id: UUID,
        body: dict,
        session: AsyncSession = Depends(get_session),
    ) -> dict:
        item_repo = SqlAlchemyItemRepository(session)
        item = await item_repo.get_by_id(item_id)
        if not item:
            raise HTTPException(404, "Item not found")
        buyer_id = body.get("buyer_id")
        if buyer_id is not None and not isinstance(buyer_id, int):
            raise HTTPException(400, "buyer_id must be an integer or null")
        item.buyer_id = buyer_id
        await item_repo.update(item)
        return {"id": str(item.id), "buyer_id": item.buyer_id}

    @router.delete("/items/{item_id}", status_code=204)
    async def delete_item(
        item_id: UUID,
        session: AsyncSession = Depends(get_session),
    ) -> None:
        item_repo = SqlAlchemyItemRepository(session)
        await item_repo.delete(item_id)

    return router


def _trip_to_dict(trip):  # type: ignore[no-untyped-def]
    return {
        "id": str(trip.id),
        "chat_id": trip.chat_id,
        "name": trip.name,
        "status": trip.status.value,
        "created_at": trip.created_at.isoformat(),
    }


def _item_to_dict(item):  # type: ignore[no-untyped-def]
    return {
        "id": str(item.id),
        "name": item.name,
        "category": item.category.value,
        "amount": item.amount,
        "is_bought": item.is_bought,
        "buyer_id": item.buyer_id,
    }
