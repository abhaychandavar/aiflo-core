from fastapi import APIRouter
from fastapi import APIRouter
from fastapi import Request
from app.controller.project import create_project, get_projects, update_project, delete_project
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR
from app.api.v1.endpoints.flow.flow import flow_router
router = APIRouter()

@router.post("")
async def create_project_rote(request: Request):
    try:
        user = request.state.user
        body = await request.json()
        res = create_project(user, body.get("name"), body.get("status"), body.get("description"), space_id=request.path_params.get("space_id"));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@router.patch("")
async def update_project_rote(request: Request):
    try:
        user = request.state.user
        body = await request.json()
        res = update_project(body.get("id"), user, body.get("name"), body.get("status"), body.get("description"), request.path_params.get("space_id"));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@router.get("")
async def get_all_projects_route(request: Request):
    try:
        user = request.state.user
        res = get_projects(user, space_id=request.path_params.get("space_id"), page=int(request.query_params.get("page", 1) or 1), minimal=request.query_params.get("minimal") == "true");
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
@router.delete("/{project_id}")
async def delete_project_route(request: Request):
    try:
        user = request.state.user
        res = delete_project(user, request.path_params.get("project_id"));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(None, e)
    
router.include_router(
    router=flow_router,
    prefix='/{project_id}/flows',
    tags=["flows"]
)