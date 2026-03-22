# backend/planner/__init__.py
# Exposes the router for registration in the main FastAPI app.
from .routes import router

__all__ = ["router"]
