from typing import Optional

from src.domain.models.base import DomainModel
from src.domain.models.permission import Permission


class Sharing(DomainModel):
    def __init__(
        self,
        calendar_id: str,
        shared_with_id: str,
        permissions: str,
        public: bool,
        id: Optional[str] = None,
    ):
        self.id = id
        self.calendar_id = calendar_id
        self.shared_with_id = shared_with_id
        self.permissions = Permission(permissions)
        self.public = public

    def get_permissions(self):
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
