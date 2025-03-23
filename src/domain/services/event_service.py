from datetime import datetime
from typing import Optional, Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.models import Calendar, Event
from src.repositories import EventRepository, SharingRepository, CalendarRepository
from src.domain.exceptions import (
    CalendarioNaoEncontradoException,
    EventoNaoEncontradoException,
    PermissaoNaoConcedidaException,
)

from src.domain.services.user_service import UserService


class EventService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = EventRepository(self.session)
        self.user_service = UserService(self.session)

    async def acessar_evento_por_id(
        self,
        event_id: str,
        logged_in_id: Optional[str],
        sharing_code: Optional[str]
    ) -> Event:

        permissao = await self.obter_permissao_de_evento(
            event_id=event_id,
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            permission_type='read'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        event = await self.repo.get(event_id)
        if not event:
            raise EventoNaoEncontradoException

        return event

    async def cadastrar_evento(
        self,
        calendar_id: str,
        titulo: str,
        descricao: Optional[str],
        inicio: datetime,
        fim: datetime,
        recorrente: Optional[bool] = False
    ) -> Event:

        calendar_repository = CalendarRepository(self.session)

        calendar = (
            await calendar_repository.get(
                calendar_id
            )
        )
        if not calendar:
            raise CalendarioNaoEncontradoException

        event = Event(
            calendar_id=calendar.get_id(),
            title=titulo,
            description=descricao,
            start_time=inicio,
            end_time=fim,
            is_recurring=recorrente
        )
        await self.repo.save(event)
        return event

    async def obter_eventos_por_calendario(
        self,
        calendar: Calendar
    ) -> Sequence[Event]:
        return await self.repo.find_all_by_calendar(calendar)

    async def atualizar_evento(
        self,
        event_id: str,
        titulo: Optional[str],
        descricao: Optional[str],
        inicio: Optional[datetime],
        fim: Optional[datetime],
        recorrente: Optional[bool],
        logged_in_id: Optional[str],
        sharing_code: Optional[str],
    ) -> None:

        permissao = await self.obter_permissao_de_evento(
            event_id=event_id,
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            permission_type='write'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        event_data = {
            'title': titulo,
            'description': descricao,
            'start_time': inicio,
            'end_time': fim,
            'is_recurring': recorrente
        }

        for key in list(event_data.keys()):
            if event_data.get(key) is None:
                event_data.pop(key, None)

        await self.repo.update(event_id, event_data)

    async def deletar_evento(
        self,
        event_id: str,
        logged_in_id: Optional[str],
        sharing_code: Optional[str]
    ) -> None:
        permissao = await self.obter_permissao_de_evento(
            event_id=event_id,
            logged_user_id=logged_in_id,
            sharing_code=sharing_code,
            permission_type='write'
        )

        if not permissao:
            raise PermissaoNaoConcedidaException

        event = await self.repo.get(event_id)
        if not event:
            raise EventoNaoEncontradoException



        await self.repo.delete(event)

    async def buscar_por_titulo(
        self,
        titulo: str
    ) -> Optional[Event]:
        return await self.repo.find_by_title(titulo)

    async def obter_permissao_de_evento(
        self,
        logged_user_id: Optional[str],
        sharing_code: Optional[str],
        event_id: str,
        permission_type: str
    ) -> bool:

        event = await self.repo.get(event_id)
        if event is None:
            return False

        calendar_repository = CalendarRepository(self.session)
        calendar = await calendar_repository.get(event.calendar_id)

        if calendar is None:
            print('Nenhum calendario encontrado')
            return False

        if calendar.public:
            print('Calendario publico')
            return True

        sharing_repository = SharingRepository(self.session)
        if sharing_code is None:
            print('Nenhum codigo de compartilhamento encontrado')
            return False

        sharing = await sharing_repository.get(sharing_code)
        if sharing is None:
            print('Nenhum compartilhamento encontrado')
            return False

        if sharing.public:
            print('Compartilhamento publico')
            return True

        if permission_type not in sharing.get_permissions():
            print('Operação não permitida')
            return False

        return (
            sharing.shared_with_id == logged_user_id and
            sharing.calendar_id == event.calendar_id
        )
