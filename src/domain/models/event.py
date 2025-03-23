from typing import Optional
from datetime import datetime

from src.domain.models.base import DomainModel


class Event(DomainModel):
    def __init__(
        self,
        calendar_id: str,
        title: str,
        description: Optional[str],
        start_time: datetime,
        end_time: datetime,
        is_recurring: Optional[bool] = False,
        id: Optional[str] = None,
    ):
        self.id = id
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
