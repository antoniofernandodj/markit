from typing import Any, Dict, Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import Calendar
from src.repositories import SharingRepository, CalendarRepository
from src.domain.exceptions import (
    CalendarioNaoEncontradoException,
    PermissaoNaoConcedidaException,
    UsuarioNaoEncontradoException
)

from src.domain.services.user_service import UserService
from src.domain.services.event_service import EventService


class CalendarService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = CalendarRepository(self.session)
        self.events_service = EventService(self.session)
        self.user_service = UserService(self.session)

    async def obter_calendario(
        self,
        calendar_id: str,
        logged_in_id: Optional[str],
        sharing_code: Optional[str]
    ) -> Calendar:

        permissao = await self.obter_permissao_de_calendario(
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            calendar_id=calendar_id,
            permission_type='read'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        calendar = await self.repo.get(calendar_id)
        if not calendar:
            raise CalendarioNaoEncontradoException

        return calendar

    async def obter_agenda(
        self,
        calendar_id: str,
        logged_in_id: Optional[str],
        sharing_code: Optional[str]
    ):
        permissao = await self.obter_permissao_de_calendario(
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            calendar_id=calendar_id,
            permission_type='read'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        calendar = await self.repo.get(calendar_id)
        if not calendar:
            raise CalendarioNaoEncontradoException

        return calendar.to_pydantic(eventos_recorrentes=True)

    async def cadastrar_calendario(
        self,
        nome: str,
        public: bool,
        user_id: str,
    ) -> Calendar:

        user = await self.user_service.repo.get(user_id)
        if not user:
            raise UsuarioNaoEncontradoException

        calendar = Calendar(nome, user.get_id(), public=public)
        await self.repo.save(calendar)
        return calendar

    async def obter_calendarios_por_usuario(
        self,
        user_id: str
    ) -> Sequence[Calendar]:
        return await self.repo.find_all_by_user(user_id)

    async def atualizar_calendario(
        self,
        calendar_id: str,
        name: str,
        sharing_code: Optional[str],
        logged_in_id: Optional[str],
        public: Optional[bool] = None,
    ) -> None:

        permissao = await self.obter_permissao_de_calendario(
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            calendar_id=calendar_id,
            permission_type='write'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        new_data: Dict[str, Any] = {'name': name}

        if public is not None:
            new_data['public'] = public

        await self.repo.update(calendar_id, new_data)

    async def deletar_calendario(
        self,
        calendar_id: str,
        logged_in_id: Optional[str],
        sharing_code: Optional[str],
    ) -> None:

        permissao = await self.obter_permissao_de_calendario(
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            calendar_id=calendar_id,
            permission_type='write'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        calendar = await self.repo.get(calendar_id)
        if not calendar:
            raise CalendarioNaoEncontradoException

        events = await self.events_service.obter_eventos_por_calendario(calendar)
        for event in events:
            await self.events_service.deletar_evento(
                event.get_id(), logged_in_id, sharing_code
            )

        await self.repo.delete(calendar)

    async def buscar_por_nome(
        self,
        nome: str
    ) -> Optional[Calendar]:
        return await self.repo.find_by_name(nome)

    async def obter_permissao_de_calendario(
        self,
        logged_user_id: Optional[str],
        sharing_code: Optional[str],
        calendar_id: str,
        permission_type: str
    ) -> bool:

        calendar = await self.repo.get(calendar_id)
        if calendar is None:
            print('Calendario não encontrado')
            return False

        if calendar.public and permission_type == 'read':
            print('Calendario publico')
            return True

        if calendar.user_id == logged_user_id:
            print('Calendario proprio do user logado')
            return True

        sharing_repository = SharingRepository(self.session)
        if sharing_code is None:
            print('Nenhum codigo de compartilhamento encontrado')
            return False

        sharing = await sharing_repository.find_by(id=sharing_code)
        if sharing is None:
            print('Nenhum compartilhamento encontrado')
            return False

        if sharing.shared_with_id == logged_user_id:
            print('Calendario compartilhado com o usuario logado')
            return True

        if sharing.public:
            print('Compartilhamento publico')
            return True

        if permission_type not in sharing.get_permissions():
            print('Operação não permitida')
            return False

        return True
