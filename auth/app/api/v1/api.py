from fastapi import APIRouter
from app.api.v1.endpoints.api import api_router

api_v1_router = APIRouter()

api_v1_router.include_router(api_router, prefix="/auth")