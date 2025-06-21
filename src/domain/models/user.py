from typing import Optional
from src.domain.models.base import DomainModel


class User(DomainModel):
    def __init__(self, name: str, email: str, password_hash: str, id: Optional[str] = None):
        self.id = id
        self.name = name
        self.email = email
        self.password_hash = password_hash
