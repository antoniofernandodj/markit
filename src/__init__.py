from contextlib import asynccontextmanager

from fastapi import FastAPI
from src.api import create_app
from src.database.entities import metadata, sync_engine



@asynccontextmanager
async def lifespan(app: FastAPI):
    metadata.create_all(bind=sync_engine)
    yield


app = create_app()


def create_all():
    metadata.create_all(sync_engine)
