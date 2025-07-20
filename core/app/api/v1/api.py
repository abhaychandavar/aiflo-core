from fastapi import APIRouter, Depends
from app.api.v1.endpoints import project
from app.api.v1.internal.api import flow_router
from app.middlewares.userAuth import validate_user_access, validate_internal_access

api_v1_router = APIRouter()

api_v1_router.include_router(
    router=flow_router,
    prefix='/internal',
    tags=["internal"],
    dependencies=[Depends(validate_internal_access)]
)

api_v1_router.include_router(project.router, prefix="/spaces/{space_id}/projects", tags=["projects"], dependencies=[Depends(validate_user_access)])