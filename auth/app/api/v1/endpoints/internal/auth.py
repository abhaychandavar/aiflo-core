from fastapi import APIRouter
from fastapi import APIRouter
from fastapi import Request
from app.controller.auth import handle_auth
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR

router = APIRouter()

@router.post("")
async def authenticate(request: Request):
    try:
        body = await request.json();
        res = await handle_auth(email = body.get('email'), method = body.get('method'), name = body.get('name'), imageURL = body.get('imageURL'), password = body.get('password'));
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
