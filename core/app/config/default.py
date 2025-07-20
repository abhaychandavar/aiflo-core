import logging
from typing import Literal, cast
import os

class Settings():
    PROJECT_NAME="core"
    VERSION="0.0.1"
    HOST=os.getenv("HOST", "localhost")
    PORT=int(os.getenv("PORT", "8080"))
    ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS")
    ENV=os.getenv("ENV", "local")
    LOG_LEVEL=logging.DEBUG
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "ALJSDh32re3rR#$RTEw(&*(rhe))")
    INTERNAL_SECRET_KEY=os.getenv("INTERNAL_SECRET_KEY", "secretKey")
    ABLY_API_KEY=os.getenv("ABLY_API_KEY")
    SERVICES={
        "flows": {
            "base-url": os.getenv("FLOWS_SERVICE_BASE_URL", "http://localhost:8080")
        }
    }

settings = Settings()