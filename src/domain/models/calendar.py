from typing import Optional, Sequence
from src.api.schema import EventResponse
from src.domain.models.base import DomainModel
from src.domain.models.event import Event
from src.domain.models.sharing import Sharing


class Calendar(DomainModel):
    events: Sequence[Event]
    def __init__(
        self,
        name: str,
        user_id: str,
        public: bool,
        id: Optional[str] = None,
    ):
        self.id = id
        self.name = name
        self.user_id = user_id
        self.public = public
        self.events: Sequence[Event] = []
        self.sharings: Sequence[Sharing] = []
