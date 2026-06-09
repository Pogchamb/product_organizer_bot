import asyncio
import logging

import uvicorn
from aiogram import Bot, Dispatcher
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from trip_master.infrastructure.config import Config
from trip_master.infrastructure.db.models import Base
from trip_master.presentation.bot.router import create_router
from trip_master.presentation.webapp.server import create_app

logger = logging.getLogger(__name__)


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    logger.info("TripMaster starting...")

    config = Config()
    engine = create_async_engine(config.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created")

    bot = Bot(token=config.bot_token)
    dp = Dispatcher()
    dp.include_router(create_router(config, session_factory))

    app = create_app(session_factory)
    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=config.host,
            port=config.port,
            log_level="info",
        )
    )

    logger.info("Starting bot polling and web server...")
    await asyncio.gather(
        dp.start_polling(bot),
        server.serve(),
    )


if __name__ == "__main__":
    asyncio.run(main())
