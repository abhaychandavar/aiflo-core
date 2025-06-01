from fastapi import APIRouter
from fastapi import APIRouter
from fastapi import Request
from app.controller.docParser import refresh_token
from app.utils.api import api_helpers 
from app.utils.api import APP_ERROR

router = APIRouter()

@router.post("/refresh")
async def refresh_auth_token(request: Request):
    try:
        body = await request.json();
        res = await refresh_token(body["token"]);
        return api_helpers.response_handler(res)
    except (Exception, APP_ERROR) as e:
        print("error", e)
        return api_helpers.response_handler(None, e)
