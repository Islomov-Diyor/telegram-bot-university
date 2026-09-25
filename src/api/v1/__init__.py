from fastapi import APIRouter
from src.api.v1.auth import router as auth_router
from src.api.v1.stats import router as stats_router
from src.api.v1.faculties import router as faculties_router
from src.api.v1.directions import router as directions_router
from src.api.v1.clubs import router as clubs_router
from src.api.v1.registrations import router as registrations_router
from src.api.v1.export import router as export_router
from src.api.v1.settings import router as settings_router

api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(stats_router)
api_v1_router.include_router(faculties_router)
api_v1_router.include_router(directions_router)
api_v1_router.include_router(clubs_router)
api_v1_router.include_router(registrations_router)
api_v1_router.include_router(export_router)
api_v1_router.include_router(settings_router)
