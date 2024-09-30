from src.database.entities import AsyncSessionFactory
from src.repositories import (
    UserRepository,
    CalendarRepository,
    SharingRepository,
    EventRepository
)

from src.domain.services import (
    AuthService,
    CalendarService,
    EventService,
    SharingService,
    UserService
)



class UnityOfWork:

    async def __aenter__(self):
        self.session = await AsyncSessionFactory().__aenter__()  # type: ignore

        self.user_repository = UserRepository(session=self.session)
        self.calendar_repository = CalendarRepository(session=self.session)
        self.event_repository = EventRepository(session=self.session)
        self.sharing_repository = SharingRepository(session=self.session)

        self.user_service = UserService(session=self.session)
        self.calendar_service = CalendarService(session=self.session)
        self.event_service = EventService(session=self.session)
        self.sharing_service = SharingService(session=self.session)
        self.auth_service = AuthService()

        return self

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            await self.session.rollback()
        else:
            try:
                await self.session.commit()
            except Exception:
                await self.session.rollback()
                raise

        await self.session.close()
