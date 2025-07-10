from fastapi import APIRouter, Depends
from app.api.v1.internal.flow import flow
flow_router = APIRouter()

flow_router.include_router(
    router=flow.router,
    prefix='/projects',
    tags=["flow"]
)