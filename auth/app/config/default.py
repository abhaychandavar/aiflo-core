import logging
from typing import Literal, cast
import os

class Settings():
    PROJECT_NAME="auth"
    VERSION="0.0.1"
    PORT=int(os.getenv("PORT", "8081"))
    ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS")
    HOST=os.getenv("HOST", "localhost")
    ENV=os.getenv("ENV", "local")
    LOG_LEVEL=logging.DEBUG
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "ALJSDh32re3rR#$RTEw(&*(rhe))")
    INTERNAL_SECRET_KEY=os.getenv("INTERNAL_SECRET_KEY", "secretKey")

settings = Settings()