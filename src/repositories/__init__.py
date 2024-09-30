from typing import Optional, Sequence
from src.database.mappers import start_mappers
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import selectinload

from src.domain.models import (
    User,
    Calendar,
    Event,
    Sharing
)
    

class Repository:
    def __init__(self, session: AsyncSession, model: type):
        try:
            start_mappers()
        except:
            pass
        self.session = session
        self.model = model

    async def get(self, id: str):

        """
        .options(  # type: ignore
            selectinload(ConsultaOverhead.dados)  # type: ignore
        )
        
        """

        try:
            stmt = select(self.model).filter_by(id=id)
            result = await self.session.execute(stmt)
            result_scalars = result.scalars()
            return result_scalars.one()
        except NoResultFound:
            return None
        
    async def find_by(self, **args):
        try:
            stmt = select(self.model).filter_by(**args)
            result = await self.session.execute(stmt)
            result_scalars = result.scalars()
            return result_scalars.one()
        except NoResultFound:
            return None
        
    async def find_all_by(self, **args):
        try:
            stmt = select(self.model).filter_by(**args)
            result = await self.session.execute(stmt)
            result_scalars = result.scalars()
            return result_scalars.all()
        except NoResultFound:
            return []

    async def all(self):
        stmt = select(self.model)
        result = await self.session.execute(stmt)
        result_scalars = result.scalars()
        return result_scalars.all()
    
    async def save(self, entity) -> None:
        self.session.add(entity)
    
    async def update(self, id, data: dict) -> None:
        entity = await self.get(id)
        for key, value in data.items():
            setattr(entity, key, value)
    
    async def delete(self, id) -> None:
        entity = await self.get(id)
        if entity:
            await self.session.delete(entity)
        else:
            raise ValueError(
                f"{self.model.__name__} with ID {id} not found"
            )


class UserRepository:
    def __init__(self, session):
        self.repo = Repository(session, User)
        self.model = User

    async def get(self, id) -> Optional[User]:
        return await self.repo.get(id)
    
    async def all(self) -> Sequence[User]:
        return await self.repo.all()
    
    async def save(self, entity: User) -> None:
        await self.repo.save(entity)
    
    async def update(self, id, data: dict) -> None:
        await self.repo.update(id, data)
    
    async def delete(self, user: User) -> None:
        await self.repo.delete(user.get_id())
    
    async def find_by_email(self, email: str) -> Optional[User]:
        return await self.repo.find_by(email=email)


class CalendarRepository:
    def __init__(self, session: AsyncSession):
        self.session= session
        self.repo = Repository(session, Calendar)
        self.model = Calendar

    async def get(self, id) -> Optional[Calendar]:
        try:
            stmt = select(self.model).filter_by(id=id).options(
                selectinload(Calendar.events)  # type: ignore
            )
            result = await self.session.execute(stmt)
            result_scalars = result.scalars()
            return result_scalars.one()
        except NoResultFound:
            return None

    async def find_by(self, **args):
        try:
            stmt = select(self.model).filter_by(**args).options(
                selectinload(Calendar.events)  # type: ignore
            )
            result = await self.session.execute(stmt)
            result_scalars = result.scalars()
            return result_scalars.one()
        except NoResultFound:
            return None
        
    async def find_all_by(self, **args):
        try:
            stmt = select(self.model).filter_by(**args).options(
                selectinload(Calendar.events)  # type: ignore
            )
            result = await self.session.execute(stmt)
            result_scalars = result.scalars()
            return result_scalars.all()
        except NoResultFound:
            return []
    
    async def all(self) -> Sequence[Calendar]:
        return await self.repo.all()
    
    async def save(self, entity: Calendar) -> None:
        await self.repo.save(entity)
    
    async def update(self, id, data: dict) -> None:
        await self.repo.update(id, data)
    
    async def delete(self, calendar: Calendar) -> None:
        await self.repo.delete(calendar.get_id())

    async def find_by_name(self, name: str) -> Optional[Calendar]:
        return await self.find_by(name=name)
    
    async def find_all_by_user(self, user_id: str) -> Sequence[Calendar]:
        return await self.find_all_by(user_id=user_id)


class EventRepository:
    def __init__(self, session):
        self.repo = Repository(session, Event)
        self.model = Event

    async def get(self, id) -> Optional[Event]:
        return await self.repo.get(id)
    
    async def all(self) -> Sequence[Event]:
        return await self.repo.all()
    
    async def save(self, entity: Event) -> None:
        await self.repo.save(entity)
    
    async def update(self, id, data: dict) -> None:
        await self.repo.update(id, data)
    
    async def delete(self, event: Event) -> None:
        await self.repo.delete(event.get_id())

    async def find_all_by_calendar(self, calendar: Calendar) -> Sequence[Event]:
        return await self.repo.find_all_by(calendar_id=calendar.get_id())
    
    async def find_by_title(self, title: str) -> Optional[Event]:
        return await self.repo.find_by(title=title)


class SharingRepository:
    def __init__(self, session):
        self.repo = Repository(session, Sharing)
        self.model = Sharing

    async def get(self, id) -> Optional[Sharing]:
        return await self.repo.get(id)
    
    async def all(self) -> Sequence[Sharing]:
        return await self.repo.all()
    
    async def find_by(self, **args):
        return await self.repo.find_by(**args)
    
    async def save(self, entity: Sharing) -> None:
        await self.repo.save(entity)
    
    async def update(self, id, data: dict) -> None:
        await self.repo.update(id, data)
    
    async def delete(self, sharing: Sharing) -> None:
        await self.repo.delete(sharing.get_id())

    async def find_all_by_calendar(self, calendar: Calendar) -> Sequence[Sharing]:
        return await self.repo.find_all_by(calendar_id=calendar.get_id())