from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from app.config.default import Settings
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.router import api_router
from app.utils.db.mongo import Mongo

logging.basicConfig(level=Settings.LOG_LEVEL)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info(f"Server is listening to PORT: {Settings.PORT}.")

    yield

    logging.info("App shutdown successful.")

def create_app() -> FastAPI:
    app = FastAPI(
        title=Settings.PROJECT_NAME,
        version=Settings.VERSION,
        lifespan=lifespan,
    )
    
    print("SETTINGS ENV", Settings.ENV[0])
    if Settings.ENV[0] == "local":
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "http://localhost:3000",
                "http://127.0.0.1:3000"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    else:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                "https://www.aiflo.dev", 
                "https://aiflo.dev", 
                "http://aiflo.dev"
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    Mongo.init()
    app.include_router(api_router)
    return app

app = create_app()