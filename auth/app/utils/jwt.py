import jwt
import datetime
import secrets
from app.config.default import settings

SECRET_KEY = settings.JWT_SECRET_KEY

def create_jwt_token(payload: dict, expires_in_minutes: int = 30*2*24) -> str:
    """Creates a JWT token with the given payload and expiration."""
    expiration_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=expires_in_minutes)
    payload['exp'] = expiration_time
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def create_refresh_token() -> str:
    """Creates a refresh token (typically a random string)."""
    refresh_token = secrets.token_urlsafe(64)
    return refresh_token

def decode_jwt_token(token: str) -> dict:
    """Decodes the JWT token and returns the payload."""
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")
    
__all__ = [
    'create_jwt_token',
    'create_refresh_token',
    'decode_jwt_token'
]