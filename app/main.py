# app/main.py — FastAPI application entrypoint with lifespan

from contextlib import asynccontextmanager
import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import get_settings
from app.routers import pages, summarization
from app.services.model_registry import ModelRegistry


# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("essenza")


# Global model registry instance
model_registry: ModelRegistry | None = None
app_start_time: float = time.time()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_registry
    settings = get_settings()

    logger.info("Starting %s v%s", settings.app_name, settings.version)

    # Record start time
    app.state.start_time = time.time()

    # Initialize model registry
    model_registry = ModelRegistry(settings)
    await model_registry.initialize()

    # Attach to app state for dependency injection
    app.state.model_registry = model_registry
    app.state.settings = settings

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down...")
    if model_registry:
        await model_registry.shutdown()
    logger.info("Shutdown complete")


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        description="Extreme Text Summarization Web Application",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )

    # Templates
    templates = Jinja2Templates(directory=str(settings.templates_dir))
    app.state.templates = templates

    # Static files
    app.mount("/static", StaticFiles(directory=str(settings.static_dir)), name="static")

    # Routers
    app.include_router(pages.router)
    app.include_router(summarization.router)

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled exception: %s", exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                },
                "request_id": getattr(request.state, "request_id", "unknown"),
            },
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )