from collections.abc import AsyncGenerator
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from trip_master.presentation.webapp.api import create_api_router


def create_app(session_factory: async_sessionmaker[AsyncSession]) -> FastAPI:
    app = FastAPI(title="TripMaster WebApp")

    async def get_session() -> AsyncGenerator[AsyncSession, None]:
        async with session_factory() as session:
            yield session

    app.include_router(create_api_router(get_session))

    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(exist_ok=True)

    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        return FileResponse(static_dir / "index.html")

    return app
