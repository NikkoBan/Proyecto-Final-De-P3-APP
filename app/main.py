from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from infrastructure.database.config import create_tables
from infrastructure.database.settings import get_settings
from presentation.api.routes.auth_routes import router as auth_router
from presentation.api.routes.task_routes import router as task_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    await create_tables()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full-stack task manager built with Clean Architecture.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(auth_router, prefix=API_PREFIX)
app.include_router(task_router, prefix=API_PREFIX)

app.mount("/static", StaticFiles(directory="presentation/static"), name="static")


@app.get("/", include_in_schema=False)
async def serve_frontend() -> FileResponse:
    return FileResponse("presentation/static/index.html")
