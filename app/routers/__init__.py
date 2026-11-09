# app/routers/__init__.py
from app.routers.pages import router as pages_router
from app.routers.summarization import router as summarization_router

__all__ = ["pages_router", "summarization_router"]