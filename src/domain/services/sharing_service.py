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
        shared_with_id: str,
        public: bool,
        permissions: str
    ) -> Sharing:

        calendar_service = CalendarService(self.session)

        calendar = (
            await calendar_service.repo.find(
                calendar_id
            )
        )
        if not calendar:
            raise CalendarioNaoEncontradoException

        usuario_repository = UserRepository(self.session)

        shared_with = (
            await usuario_repository.get(
                shared_with_id
            )
        )

        if not shared_with:
            raise UsuarioNaoEncontradoException

        sharing = await self.repo.find_by(
            calendar_id=calendar_id,
            shared_with_id=shared_with_id
        )

        if sharing:
            raise CompartilhamentoJaExistenteException

        sharing = Sharing(
            calendar_id=calendar.get_id(),
            shared_with_id=shared_with.get_id(),
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

        calendar = await calendar_repository.get(calendar_id)
        if not calendar:
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
        sharing = await self.repo.get(sharing_id)
        if not sharing:
            raise CompartilhamentoNaoEncontradoException

        await self.repo.delete(sharing)
