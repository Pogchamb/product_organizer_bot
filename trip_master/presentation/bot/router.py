import json
from uuid import UUID

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession

from trip_master.domain.entities.item import Item
from trip_master.domain.entities.trip import Trip
from trip_master.domain.enums import Category
from trip_master.infrastructure.ai.gemini_client import GeminiClient
from trip_master.infrastructure.db.item_repo import SqlAlchemyItemRepository
from trip_master.infrastructure.db.trip_repo import SqlAlchemyTripRepository
from trip_master.infrastructure.config import Config
from trip_master.presentation.bot.filters import GroupChat
from trip_master.presentation.bot.keyboards import (
    confirm_ingredients_keyboard,
    trip_detail_keyboard,
    trips_keyboard,
)

# In-memory store for generated ingredients (chat_id -> list[dict])
_pending_dishes: dict[int, list[dict]] = {}


def create_router(config: Config, session_factory: async_sessionmaker[AsyncSession]) -> Router:
    gemini = GeminiClient(config.gemini_api_key)
    router = Router()

    @router.message(Command("start"), GroupChat())
    async def cmd_start(message: Message) -> None:
        await message.reply(
            "👋 <b>TripMaster</b> — бот для координации групповых поездок.\n\n"
            "Команды:\n"
            "/new_trip <b>Название</b> — создать поездку\n"
            "/trips — список поездок\n"
            "/trip <b>ID</b> — детали поездки\n"
            "/add_item <b>Название</b> [количество] — добавить товар\n"
            "/add_dish <b>Блюдо</b> <b>персон</b> — AI-список ингредиентов\n"
            "/help — справка"
        )

    @router.message(Command("help"), GroupChat())
    async def cmd_help(message: Message) -> None:
        await message.reply(
            "📖 <b>Справка TripMaster</b>\n\n"
            "/new_trip <i>Название</i> — создать поездку\n"
            "/trips — все поездки в этом чате\n"
            "/trip <i>ID</i> — открыть поездку\n"
            "/add_item <i>Название</i> [<i>кол-во</i>] — добавить товар\n"
            "/add_dish <i>Блюдо</i> <i>персон</i> — AI подберёт ингредиенты\n\n"
            "Списком удобно управлять через WebApp (кнопка в деталях поездки)."
        )

    @router.message(Command("new_trip"), GroupChat())
    async def cmd_new_trip(message: Message) -> None:
        args = message.text.split(maxsplit=1)
        name = args[1].strip() if len(args) > 1 else ""
        if not name:
            await message.reply("❌ Укажи название: /new_trip <b>Название поездки</b>")
            return

        async with session_factory() as session:
            repo = SqlAlchemyTripRepository(session)
            trip = Trip.create(chat_id=message.chat.id, name=name)
            await repo.create(trip)

        await message.reply(f"✅ Поездка <b>{name}</b> создана!\nID: <code>{trip.id}</code>")

    @router.message(Command("trips"), GroupChat())
    async def cmd_trips(message: Message) -> None:
        async with session_factory() as session:
            repo = SqlAlchemyTripRepository(session)
            trips = await repo.get_by_chat_id(message.chat.id)

        if not trips:
            await message.reply("📭 Нет поездок. Создай: /new_trip <b>Название</b>")
            return

        kb = trips_keyboard(trips)
        await message.reply("🗂 <b>Поездки в этом чате:</b>", reply_markup=kb.as_markup())

    @router.message(Command("trip"), GroupChat())
    async def cmd_trip(message: Message) -> None:
        args = message.text.split(maxsplit=1)
        trip_id_str = args[1].strip() if len(args) > 1 else ""
        if not trip_id_str:
            await message.reply("❌ Укажи ID: /trip <b>ID</b>")
            return

        try:
            trip_id = UUID(trip_id_str)
        except ValueError:
            await message.reply("❌ Неверный формат ID")
            return

        async with session_factory() as session:
            repo = SqlAlchemyTripRepository(session)
            trip = await repo.get_by_id(trip_id)

        if not trip:
            await message.reply("❌ Поездка не найдена")
            return

        kb = trip_detail_keyboard(str(trip.id), config.webapp_url)
        await message.reply(
            f"🏕 <b>{trip.name}</b>\n"
            f"ID: <code>{trip.id}</code>\n"
            f"Статус: {trip.status.value}\n"
            f"Создана: {trip.created_at:%d.%m.%Y %H:%M}",
            reply_markup=kb.as_markup(),
        )

    @router.message(Command("add_item"), GroupChat())
    async def cmd_add_item(message: Message) -> None:
        parts = message.text.split(maxsplit=1)
        args = parts[1].strip() if len(parts) > 1 else ""
        if not args:
            await message.reply("❌ Укажи: /add_item <b>Название</b> [количество]")
            return

        parts = args.split(maxsplit=1)
        name = parts[0]
        amount = parts[1].strip() if len(parts) > 1 else ""

        async with session_factory() as session:
            trip_repo = SqlAlchemyTripRepository(session)
            trip = await trip_repo.get_active_by_chat_id(message.chat.id)

            if not trip:
                await message.reply(
                    "❌ Нет активной поездки. Создай: /new_trip <b>Название</b>"
                )
                return

            item = Item.create(trip_id=trip.id, name=name, category=Category.food, amount=amount)
            item_repo = SqlAlchemyItemRepository(session)
            await item_repo.create(item)

        await message.reply(f"✅ <b>{name}</b> добавлен в <b>{trip.name}</b>")

    @router.message(Command("add_dish"), GroupChat())
    async def cmd_add_dish(message: Message) -> None:
        parts = message.text.split(maxsplit=1)
        args = parts[1].strip() if len(parts) > 1 else ""
        if not args:
            await message.reply("❌ Укажи: /add_dish <b>Блюдо</b> <b>количество персон</b>")
            return

        parts = args.rsplit(maxsplit=1)
        if len(parts) < 2 or not parts[1].isdigit():
            await message.reply("❌ Пример: /add_dish <b>Борщ</b> <b>4</b>")
            return

        dish = parts[0].strip()
        persons = int(parts[1])

        await message.reply(f"⏳ Генерирую ингредиенты для <b>{dish}</b>...")

        try:
            ingredients = await gemini.generate_ingredients(dish, persons)
        except Exception as e:
            await message.reply(f"❌ Ошибка AI: {e}")
            return

        if not ingredients:
            await message.reply("❌ AI не вернул ингредиенты. Попробуй ещё раз.")
            return

        _pending_dishes[message.chat.id] = ingredients

        lines = [f"🧂 <b>{dish}</b> — ингредиенты:"]
        for ing in ingredients:
            lines.append(f"• {ing['name']} — {ing.get('amount', '')}")
        lines.append("")

        data_key = f"{dish}||{persons}"
        kb = confirm_ingredients_keyboard(dish, data_key)

        await message.reply("\n".join(lines), reply_markup=kb.as_markup())

    @router.callback_query(F.data.startswith("confirm_dish:"))
    async def cb_confirm_dish(callback: CallbackQuery) -> None:
        ingredients = _pending_dishes.pop(callback.message.chat.id, None)
        if not ingredients:
            await callback.message.edit_text("❌ Данные устарели. Попробуй /add_dish заново.")
            return

        async with session_factory() as session:
            trip_repo = SqlAlchemyTripRepository(session)
            trip = await trip_repo.get_active_by_chat_id(callback.message.chat.id)

            if not trip:
                await callback.message.edit_text(
                    "❌ Нет активной поездки. Создай: /new_trip <b>Название</b>"
                )
                return

            items = [
                Item.create(
                    trip_id=trip.id,
                    name=ing["name"],
                    category=Category.food,
                    amount=ing.get("amount", ""),
                )
                for ing in ingredients
            ]
            item_repo = SqlAlchemyItemRepository(session)
            await item_repo.create_many(items)

        await callback.message.edit_text(
            f"✅ {len(items)} ингредиентов добавлено в <b>{trip.name}</b>!"
        )
        await callback.answer()

    @router.callback_query(F.data.startswith("regenerate:"))
    async def cb_regenerate(callback: CallbackQuery) -> None:
        data = callback.data.removeprefix("regenerate:")
        parts = data.split("||")
        if len(parts) != 2:
            await callback.answer("Ошибка данных")
            return

        dish, persons_str = parts
        persons = int(persons_str)

        await callback.message.edit_text(f"⏳ Генерирую заново <b>{dish}</b>...")

        try:
            ingredients = await gemini.generate_ingredients(dish, persons)
        except Exception as e:
            await callback.message.edit_text(f"❌ Ошибка AI: {e}")
            return

        if not ingredients:
            await callback.message.edit_text("❌ AI не вернул ингредиенты. Попробуй ещё раз.")
            return

        _pending_dishes[callback.message.chat.id] = ingredients

        lines = [f"🧂 <b>{dish}</b> — ингредиенты:"]
        for ing in ingredients:
            lines.append(f"• {ing['name']} — {ing.get('amount', '')}")
        lines.append("")

        kb = confirm_ingredients_keyboard(dish, data)
        await callback.message.edit_text("\n".join(lines), reply_markup=kb.as_markup())
        await callback.answer()

    @router.callback_query(F.data == "cancel_dish")
    async def cb_cancel_dish(callback: CallbackQuery) -> None:
        _pending_dishes.pop(callback.message.chat.id, None)
        await callback.message.edit_text("❌ Отменено")
        await callback.answer()

    @router.callback_query(F.data == "close")
    async def cb_close(callback: CallbackQuery) -> None:
        await callback.message.delete()
        await callback.answer()

    return router
