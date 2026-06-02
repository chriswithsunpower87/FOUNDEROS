"""
File: app/api/v1/router.py
Purpose: Aggregates all v1 route modules into a single APIRouter.
Responsibilities:
  - Import and include all endpoint routers
  - Mounted at /api/v1 in main.py
Dependencies:
  - All route modules in app/api/v1/
"""

from fastapi import APIRouter

from app.api.v1 import auth, export, ideas, reports

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(ideas.router)
api_router.include_router(reports.router)
api_router.include_router(export.router)
