

from datetime import datetime
from typing import Optional, Sequence
from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class CalendarCreateRequest(BaseModel):
    name: str
    user_id: str
    public: bool


class EventCreateRequest(BaseModel):
    calendar_id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    is_recurring: Optional[bool] = False


class EventUpdateRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    is_recurring: Optional[bool] = None


class SharingCreateRequest(BaseModel):
    calendar_id: str
    shared_with_id: str
    permissions: str
    public: bool


class SharingUpdateRequest(BaseModel):
    permissions: str
    public: bool


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr


class EventResponse(BaseModel):
    id: str
    calendar_id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    is_recurring: Optional[bool] = False


class CalendarResponse(BaseModel):
    id: str
    name: str
    user_id: str
    events: Sequence[EventResponse]
    public: bool


class SharingResponse(BaseModel):
    id: str
    calendar_id: str
    shared_with_id: str
    permissions: str
    public: bool

