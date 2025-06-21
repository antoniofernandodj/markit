from typing import Any, Sequence
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
        from src.database.mappers import start_mappers

        start_mappers()

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
        from src.database.mappers import clear_mappers


        if exc_type is not None:
            await self.session.rollback()
        else:
            try:
                await self.session.commit()
            except Exception:
                await self.session.rollback()
                raise

        await self.session.close()
        clear_mappers()

    async def commit(self):
        await self.session.commit()


    async def refresh(self, items: Sequence[Any]):
        for item in items:
            await self.session.refresh(item)
