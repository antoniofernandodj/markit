from src.api import create_app
from src.database.entities import metadata, sync_engine


app = create_app()


def create_all():
    metadata.create_all(sync_engine)
