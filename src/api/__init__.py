from fastapi import FastAPI


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

    return app
