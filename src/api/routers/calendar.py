from fastapi import APIRouter, status, Request, HTTPException
from typing import Optional, Sequence
from src.api import depends
from src.api.schema import (
    ApiResponse,
    CalendarCreateRequest,
    CalendarResponse,
    CalendarsResponse
)
from src.api.utils import get_logged_in_id, get_token
from fastapi_utils.cbv import cbv
from src.domain.models.user import User
from src.uow import UnityOfWork


router = APIRouter(tags=['Calendar'])


@cbv(router)
class CalendarController:

    uow: UnityOfWork = depends.uow
    request: Request
    token: Optional[str] = depends.token

    @router.post(
        "/calendarios/",
        response_model=ApiResponse,
        summary='Cadastrar um novo calendário',
        description="Permite cadastrar um novo calendário associado "
        "a um usuário. O usuário deve existir no sistema.",
        status_code=status.HTTP_201_CREATED
    )
    async def cadastrar_calendario(
        self,
        body: CalendarCreateRequest
    ) -> ApiResponse:

        if (user_id := await get_logged_in_id(self.token)) is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Usuário não autenticado"
            )

        calendario = await self.uow.calendar_service.cadastrar_calendario(
            nome=body.name,
            public=body.public,
            user_id=user_id
        )

        await self.uow.commit()
        await self.uow.refresh([calendario])

        return ApiResponse(
            detail="Calendário cadastrado com sucesso",
            resource={"id": calendario.id}
        )

    @router.get(
        "/calendarios/{calendar_id}",
        response_model=CalendarResponse,
        summary='Obter um calendário por ID',
        description='Busca um calendário específico pelo seu ID, '
        'verificando as permissões do usuário logado ou do código de '
        'compartilhamento fornecido.',
        status_code=status.HTTP_200_OK
    )
    async def acessar_calendario(
        self,
        calendar_id: str,
        eventos_recorrentes: Optional[bool] = None
    ) -> CalendarResponse:

        calendar = await self.uow.calendar_service.obter_calendario(
            calendar_id=calendar_id,
            logged_in_id=await get_logged_in_id(self.token),
            sharing_code=self.request.headers.get('sharing_code')
        )

        return CalendarResponse.model_validate_calendar_response(calendar, eventos_recorrentes)

    @router.get(
        "/calendarios/agendas/{calendar_id}",
        response_model=CalendarResponse,
        summary='Obter uma agenda por ID',
        description='Busca uma agenda (calendario de eventos recorrentes) '
        'específica pelo seu ID, verificando as permissões '
        'do usuário logado ou do código de compartilhamento fornecido.',
        status_code=status.HTTP_200_OK
    )
    async def acessar_agenda(
        self,
        calendar_id: str,
        eventos_recorrentes: Optional[bool] = None
    ) -> CalendarResponse:

        agenda = await self.uow.calendar_service.obter_calendario(
            calendar_id=calendar_id,
            logged_in_id=await get_logged_in_id(self.token),
            sharing_code=self.request.headers.get('sharing_code')
        )

        return CalendarResponse.model_validate_calendar_response(agenda, True)

    @router.get(
        "/agendas/",
        summary='Listar agendas do usuário logado',
        description='Retorna uma lista de todas as agendas pertencentes '
        'ao usuário logado.',
        response_model=CalendarsResponse,
        status_code=status.HTTP_200_OK
    )
    async def listar_agendas(
        self,
        current_user: User = depends.current_user,
    ) -> CalendarsResponse:

        return CalendarsResponse(calendars=[
            CalendarResponse.model_validate_calendar_response(calendar, True)
            for calendar in (
                await self.uow.calendar_service.obter_calendarios_por_usuario(
                    current_user.get_id()
                )
            )
        ])

    @router.get(
        "/calendarios/",
        summary='Listar calendários do usuário logado',
        description='Retorna uma lista de todos os calendários pertencentes '
        'ao usuário logado.',
        response_model=CalendarsResponse,
        status_code=status.HTTP_200_OK
    )
    async def listar_calendarios(
        self,
        current_user: User = depends.current_user,
    ) -> CalendarsResponse:

        return CalendarsResponse(calendars=[
            CalendarResponse.model_validate_calendar_response(calendar)
            for calendar in (
                await self.uow.calendar_service.obter_calendarios_por_usuario(
                    current_user.get_id()
                )
            )
        ])

    @router.delete(
        "/calendarios/{calendar_id}",
        response_model=ApiResponse,
        summary='Deletar um calendário por ID',
        description='Remove um calendário específico pelo seu ID, '
        'verificando as permissões do usuário logado ou do código de '
        'compartilhamento fornecido.',
        status_code=status.HTTP_200_OK
    )
    async def deletar_calendario(
        self,
        calendar_id: str,
    ) -> ApiResponse:

        await self.uow.calendar_service.deletar_calendario(
            calendar_id=calendar_id,
            logged_in_id=await get_logged_in_id(self.token),
            sharing_code=self.request.headers.get('sharing_code')
        )
        await self.uow.commit()
        return ApiResponse(detail="Calendário removido com sucesso")

    @router.put(
        "/calendarios/{calendar_id}",
        response_model=ApiResponse,
        summary='Atualizar um calendário por ID',
        description='Atualiza o nome de um calendário específico, '
        'verificando as permissões do usuário logado ou do código '
        'de compartilhamento fornecido.',
        status_code=status.HTTP_200_OK
    )
    async def atualizar_calendario(
        self,
        calendar_id: str,
        name: str,
    ) -> ApiResponse:

        await self.uow.calendar_service.atualizar_calendario(
            calendar_id=calendar_id,
            name=name,
            sharing_code=self.request.headers.get('sharing_code'),
            logged_in_id=await get_logged_in_id(self.token)
        )
        await self.uow.commit()
        return ApiResponse(detail="Calendário atualizado com sucesso")
