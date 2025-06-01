from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from app.config.default import settings
from app.utils.api import api_helpers,APP_ERROR,StatusCode
from app.utils.jwt import decode_jwt_token

async def validate_internal_access(request: Request):
    try:
        token = request.headers.get("Authorization")
        if not token or 'Bearer' not in token:
            raise APP_ERROR(status_code=StatusCode.UNAUTHORIZED, code='app/invalid-auth-token', message='Invalid authorization header')
        token = token.split()[1]
        if token != settings.INTERNAL_SECRET_KEY:
            raise HTTPException(
                status_code=StatusCode.UNAUTHORIZED,
                detail="Unauthorized access"
            )
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(error=e, data={})

async def validate_user_access(request: Request):
    try:
        token = request.headers.get('Authorization')
        if not token or 'Bearer' not in token:
            raise APP_ERROR(status_code=StatusCode.UNAUTHORIZED, code='app/invalid-auth-token', message='Invalid authorization header')
        token = token.split()[1]
        payload = decode_jwt_token(token)
        request.state.user = payload
    except (Exception, APP_ERROR) as e:
        return api_helpers.response_handler(error=e, data={})

__all__ = [
    "validate_internal_access",
    "validate_user_access",
]