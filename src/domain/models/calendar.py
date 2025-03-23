from typing import Optional, Sequence
from src.domain.models.base import DomainModel
from src.domain.models.event import Event


class Calendar(DomainModel):
    events: Sequence[Event]
    def __init__(
        self,
        name: str,
        user_id: str,
        public: bool,
        events: Sequence[Event] = [],
        id: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.events = events
        self.public = public

    def to_pydantic(self, eventos_recorrentes: Optional[bool] = None):
        from src.api.schema import CalendarResponse

        if eventos_recorrentes is None:
            events = [event.to_pydantic() for event in self.events]

        else:
            events = [
                event.to_pydantic() for event in self.events
                if event.is_recurring == eventos_recorrentes
            ]

        return CalendarResponse(
            id=self.get_id(),
            name=self.name,
            user_id=self.user_id,
            public=self.public,
            events=events
        )
