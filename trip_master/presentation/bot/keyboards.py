from aiogram.utils.keyboard import InlineKeyboardBuilder

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


def confirm_ingredients_keyboard(dish_id: str) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Добавить", callback_data=f"confirm_dish:{dish_id}")
    builder.button(text="🔄 Заново", callback_data=f"regenerate:{dish_id}")
    builder.button(text="❌ Отмена", callback_data=f"cancel_dish:{dish_id}")
    builder.adjust(2)
    return builder
