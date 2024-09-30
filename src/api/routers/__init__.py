from . import auth, calendar, event, sharing, user


from .auth import router as auth_router
from .calendar import router as calendar_router
from .event import router as event_router
from .sharing import router as sharing_router
from .user import router as user_router
