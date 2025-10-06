from typing import Literal, Optional

from src.domain.models.base import DomainModel
from src.domain.models.permission import Permission


class Sharing(DomainModel):
    def __init__(
        self,
        calendar_id: str,
        shared_with_email: str,
        permissions: Literal['read', 'write', 'read_write'],
        public: bool,
        id: Optional[str] = None,
    ):
        self.id = id
        self.calendar_id = calendar_id
        self.shared_with_email = shared_with_email
        self.permissions = Permission(permissions)
        self.public = public

    def get_permissions(self):
        return self.permissions.value
