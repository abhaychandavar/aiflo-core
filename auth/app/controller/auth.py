import logging
from app.utils.db.models.user import Users
from bson.objectid import ObjectId
from typing import Optional
from app.utils.stringHelpers import generate_password
from app.utils.crypto import hash_password
from app.utils.api import APP_ERROR, StatusCode
from app.utils.jwt import create_jwt_token, create_refresh_token
from app.utils.db.models.refreshToken import RefreshTokens

async def handle_auth(email: str, method: str, name: Optional[str], imageURL: Optional[str], password: Optional[str]):
    if not password:
        password = generate_password(16)
    
    hashed_password = hash_password(password)

    curr_user = Users.objects.filter(email=email).first()

    user_dict = None

    if not curr_user:
        user_obj = Users(
            name = name, 
            email = email,
            password = hashed_password,
            imageURL = imageURL,
            isActive = True,
            authMethod = method
        )
        res = user_obj.save()
        if not res:
            raise APP_ERROR(code="app/could-not-create-user", status_code=StatusCode.SOMETHING_WENT_WRONG)
        user_dict = res.to_dict()
    else:
        user_dict = curr_user.to_dict()
    
    access_token = create_jwt_token(user_dict)
    refresh_token = create_refresh_token()

    refresh_token_obj = RefreshTokens(
        user = ObjectId(user_dict["_id"]),
        token = refresh_token,
    )
    refresh_token_obj.save();
    
    return {
        "accessToken": access_token,
        "refreshToken": refresh_token,
        "user": user_dict
    }

async def refresh_token(token: str):
    refresh_token = RefreshTokens.objects.filter(token=token).first()
    if not refresh_token:
        raise APP_ERROR(code="app/token-invalid", status_code=StatusCode.UNAUTHORIZED)
    refresh_token_dict = refresh_token.to_dict()
    user_id = refresh_token_dict["user"]
    user = Users.objects.get(id=ObjectId(user_id))
    if not user:
        raise APP_ERROR(code="app/user-doesnt-exist", status_code=StatusCode.NOT_FOUND)
    user_dict = user.to_dict()
    access_token = create_jwt_token(user_dict)
    new_refresh_token = create_refresh_token()
    refresh_token_db_obj = RefreshTokens(
        user = ObjectId(user_dict["_id"]),
        token = new_refresh_token,
    )
    refresh_token_db_obj.save();
    return {
        "accessToken": access_token,
        "refreshToken": new_refresh_token,
        "user": user_dict
    }