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
