

from datetime import datetime
from typing import Any, Dict, Optional, Sequence, List
from pydantic import BaseModel, EmailStr

from src.domain.models.calendar import Calendar


class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserUpdateRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class CalendarCreateRequest(BaseModel):
    name: str
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
    shared_with_email: str
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

    @classmethod
    def model_validate_calendar_response(cls, model: Calendar, eventos_recorrentes: Optional[bool] = None):

        if eventos_recorrentes is None:
            events = [EventResponse.model_validate(event) for event in model.events]

        else:
            events = [
                EventResponse.model_validate(event) for event in model.events
                if event.is_recurring == eventos_recorrentes
            ]

        return CalendarResponse(
            id=model.get_id(),
            name=model.name,
            user_id=model.user_id,
            public=model.public,
            events=events
        )


class CalendarsResponse(BaseModel):
    calendars: List[CalendarResponse]


class SharingResponse(BaseModel):
    id: str
    calendar_id: str
    shared_with_email: str
    permissions: str
    public: bool


class SharingsResponse(BaseModel):
    sharings: List[SharingResponse]


class ApiResponse(BaseModel):
    detail: str
    resource: Optional[Dict[str, Any]] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
