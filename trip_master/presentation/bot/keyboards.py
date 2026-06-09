from aiogram.utils.keyboard import InlineKeyboardBuilder

from trip_master.domain.entities.item import Item
from trip_master.domain.entities.trip import Trip


def trips_keyboard(trips: list[Trip]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for trip in trips:
        builder.button(text=trip.name, callback_data=f"trip:{trip.id}")
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(1)
    return builder


def trip_detail_keyboard(trip_id: str, webapp_url: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="📋 Открыть список",
        web_app=dict(url=f"{webapp_url}/?trip_id={trip_id}"),
    )
    builder.button(text="❌ Закрыть", callback_data="close")
    builder.adjust(1)
    return builder


def items_keyboard(items: list[Item]) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for item in items:
        status = "✅" if item.is_bought else "⬜"
        buyer = f" — {item.buyer_id}" if item.buyer_id else ""
        text = f"{status} {item.name} {item.amount}{buyer}"
        builder.button(text=text, callback_data=f"item:{item.id}")
    builder.adjust(1)
    return builder


def confirm_ingredients_keyboard(dish: str, data: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Добавить", callback_data=f"confirm_dish:{data}")
    builder.button(text="🔄 Заново", callback_data=f"regenerate:{data}")
    builder.button(text="❌ Отмена", callback_data="cancel_dish")
    builder.adjust(2)
    return builder
