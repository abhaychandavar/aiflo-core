from fastapi import APIRouter, Depends
from app.api.v1.endpoints.internal.docProcessor import router as internal_router
from app.api.v1.endpoints.storage.storage import router as storage_router
from app.middlewares.userAuth import validate_internal_access, validate_user_access

api_router = APIRouter()

api_router.include_router(
    router=internal_router, 
    prefix="/internal", 
    dependencies=[Depends(validate_internal_access)],
    tags=["Internal"]
)

api_router.include_router(
    router=storage_router, 
    prefix="/storage", 
    dependencies=[Depends(validate_user_access)],
    tags=["Storage"]
)
