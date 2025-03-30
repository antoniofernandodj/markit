from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import User
from src.repositories import EventRepository, UserRepository, CalendarRepository
from src.domain.exceptions import (
    EmailJaCadastradoException,
    UsuarioNaoEncontradoException
)

from src.domain.services.auth_service import AuthService

class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = UserRepository(self.session)
        self.calendar_repository = CalendarRepository(self.session)
        self.events_repository = EventRepository(self.session)
        self.auth_service = AuthService()

    async def remover_usuario(
        self,
        user: User
    ) -> None:
        calendars = await self.calendar_repository.find_all_by_user(user.get_id())
        for calendar in calendars:
            events = await self.events_repository.find_all_by_calendar(calendar)
            for event in events:

                await self.events_repository.delete(event)
            await self.calendar_repository.delete(calendar)
        await self.repo.delete(user)

    async def cadastrar_usuario(
        self,
        nome: str,
        email: str,
        senha: str
    ) -> User:

        existing_user = await self.repo.find_by_email(email)
        if existing_user:
            raise EmailJaCadastradoException

        hashed = self.auth_service.generate_hash(senha)
        user = User(nome, email, hashed)
        await self.repo.save(user)
        return user

    async def atualizar_dados_de_usuario(
        self,
        user_id: str,
        nome: Optional[str] = None,
        email: Optional[str] = None,
        senha: Optional[str] = None
    ) -> None:

        dados = {
            'name': nome,
            'email': email,
        }

        if not await self.repo.get(user_id):
            raise UsuarioNaoEncontradoException

        if email:
            existing_user = await self.repo.find_by_email(email)
            if existing_user and existing_user.get_id() != user_id:
                raise EmailJaCadastradoException

        if senha:
            dados['password_hash'] = self.auth_service.generate_hash(senha)

        await self.repo.update(user_id, {
            key: value for key, value in dados.items() if value is not None
        })

    async def obter_por_email(self, email: str) -> Optional[User]:
        return await self.repo.find_by_email(email)
