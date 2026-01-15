import os
from dataclasses import dataclass
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging

load_dotenv()

logger = logging.getLogger(__name__)


@dataclass
class Settings:
    secret_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))


settings = Settings()

MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
ORIGIN_URL = os.getenv("ORIGIN_URL")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4.1-nano")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application...")
    
    # MongoDB
    app.mongodb_client = AsyncIOMotorClient(MONGODB_URL)
    app.mongodb = app.mongodb_client[DATABASE_NAME]
    
    # Initialize PostgreSQL checkpointer
    from app.graph.graph import init_checkpointer
    await init_checkpointer()
    
    # Start graph service cleanup loop
    from app.services.graph_dependencies import get_graph_service
    graph_service = get_graph_service()
    await graph_service.start()
    
    logger.info("Application started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    
    # Stop graph service
    from app.services.graph_dependencies import get_graph_service
    graph_service = get_graph_service()
    await graph_service.stop()

    # Close checkpointer
    from app.graph.graph import close_checkpointer
    await close_checkpointer()
    
    # Close MongoDB
    app.mongodb_client.close()
    
    logger.info("Application shutdown complete")