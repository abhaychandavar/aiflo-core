import logging
from typing import Literal, cast
import os

class Settings():
    PROJECT_NAME="doc-processor"
    VERSION="0.0.1"
    PORT=int(os.getenv("PORT", "8083"))
    HOST=os.getenv("HOST", "localhost")
    ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS")
    ENV=os.getenv("ENV", "local")
    LOG_LEVEL=logging.DEBUG
    JWT_SECRET_KEY=os.getenv("JWT_SECRET_KEY", "ALJSDh32re3rR#$RTEw(&*(rhe))")
    INTERNAL_SECRET_KEY=os.getenv("INTERNAL_SECRET_KEY", "secretKey")
    S3_SIGNED_URL_EXPIRY=int(os.getenv("S3_SIGNED_URL_EXPIRY", "300"))
    FLOW_SERVICE_BASE_URL=os.getenv("FLOW_SERVICE_BASE_URL", "http://localhost:8080")
    QSTASH_API_KEY=os.getenv("QSTASH_API_KEY")
    SERVICES={
        "doc-processor": {
            "event-url": f"{os.getenv("DOC_PROCESSOR_BASE_URL", "http://localhost:8083")}/api/v1/doc-processor/internal/event?secretKey={os.getenv("INTERNAL_SECRET_KEY", "secretKey")}"
        }
    }

settings = Settings()