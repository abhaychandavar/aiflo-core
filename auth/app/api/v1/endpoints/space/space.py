from fastapi import APIRouter
from fastapi import APIRouter
from fastapi import Request
from app.controller.space import create_space, get_spaces
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR

space_router = APIRouter()

@space_router.post("")
async def create_space_route(request: Request):
    try:
        user = user = request.state.user
        body = await request.json();
        res = create_space(user=user, name=body.get('name'));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
    
@space_router.get("")
async def get_spaces_route(request: Request):
    try:
        user = user = request.state.user
        res = get_spaces(user=user);
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)