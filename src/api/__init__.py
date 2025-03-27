from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_app():

    app = FastAPI()

    from src.api import routers
    from src.api.utils import register_exceptions

    app.include_router(routers.event_router)
    app.include_router(routers.calendar_router)
    app.include_router(routers.sharing_router)
    app.include_router(routers.user_router)
    app.include_router(routers.auth_router)

    register_exceptions(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
