from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import Sharing
from src.repositories import SharingRepository, UserRepository, CalendarRepository
from src.domain.exceptions import (
    CalendarioNaoEncontradoException,
    CompartilhamentoJaExistenteException,
    CompartilhamentoNaoEncontradoException,
    UsuarioNaoEncontradoException
)

from src.domain.services.calendar_service import CalendarService


class SharingService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = SharingRepository(self.session)

    async def compartilhar_calendario(
        self,
        calendar_id: str,
        shared_with_email: str,
        public: bool,
        permissions: str
    ) -> Sharing:

        calendar_service = CalendarService(self.session)

        if not (calendar := (
            await calendar_service.repo.find(
                calendar_id
            )
        )):
            raise CalendarioNaoEncontradoException

        if (await self.repo.find_by(
            calendar_id=calendar_id,
            shared_with_email=shared_with_email
        )):
            raise CompartilhamentoJaExistenteException

        sharing = Sharing(
            calendar_id=calendar.get_id(),
            shared_with_email=shared_with_email,
            permissions=permissions,
            public=public
        )
        await self.repo.save(sharing)
        return sharing

    async def obter_compartilhamentos_por_calendario(
        self,
        calendar_id: str
    ) -> Sequence[Sharing]:

        calendar_repository = CalendarRepository(self.session)

        if not (calendar := await calendar_repository.get(calendar_id)):
            raise CalendarioNaoEncontradoException

        return await self.repo.find_all_by_calendar(calendar)

    async def atualizar_compartilhamento(
        self,
        sharing_id: str,
        permissions: str,
        public: bool
    ) -> None:

        await self.repo.update(sharing_id, {
            "permissions": permissions,
            "public": public
        })

    async def deletar_compartilhamento(
        self,
        sharing_id: str
    ) -> None:

        if not (sharing := await self.repo.get(sharing_id)):
            raise CompartilhamentoNaoEncontradoException

        await self.repo.delete(sharing)
