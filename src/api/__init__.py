from fastapi import FastAPI

def create_app():

    app = FastAPI()

    from src.api import routers

    app.include_router(routers.event_router)
    app.include_router(routers.calendar_router)
    app.include_router(routers.sharing_router)
    app.include_router(routers.user_router)
    app.include_router(routers.auth_router)

    return app
