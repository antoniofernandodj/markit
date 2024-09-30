import enum
from pydantic import BaseModel, EmailStr
from typing import Optional, Sequence, Union
from datetime import datetime


class Permission(enum.Enum):
    read = 'read'
    write = 'write'
    read_write = 'read_write'



class DomainModel:
    def __str__(self) -> str:
        fields = ', '.join(f'{k}={v}' for k, v in vars(self).items() if not k.startswith('_sa'))
        return f'{self.__class__.__name__}({fields})'

    def __repr__(self) -> str:
        return self.__str__()

    def get_id(self) -> str:
        return getattr(self, 'id')


class User(DomainModel):
    def __init__(self, name: str, email: str, password_hash: str):
        self.name = name
        self.email = email
        self.password_hash = password_hash

    def to_pydantic(self):
        from src.api.schema import UserResponse

        return UserResponse(
            id=self.get_id(),
            name=self.name,
            email=self.email
        )
    


class Event(DomainModel):
    def __init__(
        self,
        calendar_id: str,
        title: str,
        description: Optional[str],
        start_time: datetime,
        end_time: datetime,
        is_recurring: Optional[bool] = False
    ):
        self.calendar_id = calendar_id
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.is_recurring = is_recurring


    def to_pydantic(self):
        from src.api.schema import EventResponse

        return EventResponse(
            id=self.get_id(),
            calendar_id=self.calendar_id,
            title=self.title,
            description=self.description,
            start_time=self.start_time,
            end_time=self.end_time,
            is_recurring=self.is_recurring
        )


class Calendar(DomainModel):
    events: Sequence[Event]
    def __init__(self, name: str, user_id: str, public: bool, events: Sequence[Event] = []):
        self.name = name
        self.user_id = user_id
        self.events = events
        self.public = public

    def to_pydantic(self):
        from src.api.schema import CalendarResponse

        return CalendarResponse(
            id=self.get_id(),
            name=self.name,
            user_id=self.user_id,
            public=self.public,
            events=[event.to_pydantic() for event in self.events]
        )


class Sharing(DomainModel):
    def __init__(
        self,
        calendar_id: str,
        shared_with_id: str,
        permissions: Union[Permission, str],
        public: bool
    ):
        self.calendar_id = calendar_id
        self.shared_with_id = shared_with_id
        self.permissions = permissions
        self.public = public

    def get_permissions(self):
        if isinstance(self.permissions, str):
            return self.permissions
        else:
            return self.permissions.value

    def to_pydantic(self):
        from src.api.schema import SharingResponse

        return SharingResponse(
            id=self.get_id(),
            calendar_id=self.calendar_id,
            shared_with_id=self.shared_with_id,
            permissions=self.get_permissions(),
            public=self.public
        )