from fastapi import APIRouter, Depends, Request
from app.api.v1.endpoints.internal.auth import router
from app.api.v1.endpoints.open.auth import router as open_router
from app.middlewares.userAuth import validate_internal_access
from app.utils.api import api_helpers, APP_ERROR

api_router = APIRouter()

api_router.include_router(
    router, 
    prefix="/internal", 
    dependencies=[Depends(validate_internal_access)],
    tags=["Internal"]
)

api_router.include_router(
	router=open_router,
	prefix="/open",
	tags=["Open"],
)