from typing import Optional

from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseSettings

from app.models.room import Room

from urllib.parse import quote_plus

from rich.console import Console
import os

console = Console()

async def initiate_database():
    mongo_uri = os.environ["MONGO_URI"]
    console.log("mongo_uri:", mongo_uri)
    client = AsyncIOMotorClient(mongo_uri)
    await init_beanie(database=client.get_default_database(),
                      document_models=[Room])
