from __future__ import annotations
from fastapi import FastAPI
from app.infra.logging import configure_logging
from app.infra.errors import AppError, app_error_handler
from app.api.routes import blobs


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title="Rekaz Drive", version="1.0.0")
    app.add_exception_handler(AppError, app_error_handler)
    app.include_router(blobs.router)
    return app


app = create_app()
