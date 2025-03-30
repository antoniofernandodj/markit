from fastapi import APIRouter, Request
from typing import Optional

from fastapi.params import Depends
from src.api.schema import ApiResponse, EventCreateRequest, EventResponse, EventUpdateRequest
from src.api import depends
from src.api.utils import get_logged_in_id, get_token
from fastapi_utils.cbv import cbv

from src.uow import UnityOfWork


router = APIRouter(tags=['Event'])


@cbv(router)
class EventController:

    uow: UnityOfWork = depends.uow
    request: Request

    @router.get(
        "/eventos/{event_id}",
        response_model=EventResponse,
        summary="Obter evento por ID",
        description="Retorna um evento específico pelo ID, verificando "
        "as permissões do usuário logado ou do código de compartilhamento."
    )
    async def acessar_evento_por_id(
        self,
        event_id: str,
        token: Optional[str] = depends.token
    ) -> EventResponse:

        event = await self.uow.event_service.acessar_evento_por_id(
            event_id=event_id,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=self.request.headers.get('sharing_code')
        )

        return event.to_pydantic()


    @router.post(
        "/eventos/",
        response_model=ApiResponse,
        summary="Cadastrar um novo evento",
        description="Cria um novo evento para o calendário especificado, "
        "desde que o calendário exista."
    )
    async def cadastrar_evento(self, body: EventCreateRequest) -> ApiResponse:

        evento = await self.uow.event_service.cadastrar_evento(
            calendar_id=body.calendar_id,
            titulo=body.title,
            descricao=body.description,
            inicio=body.start_time,
            fim=body.end_time,
            recorrente=body.is_recurring
        )
        await self.uow.commit()
        await self.uow.session.refresh(evento)
        return ApiResponse(
            detail="Evento cadastrado com sucesso!",
            resource={'id': evento.id}
        )


    @router.delete(
        "/eventos/{event_id}",
        response_model=ApiResponse,
        summary="Deletar evento por ID",
        description="Remove um evento específico, verificando as "
        "permissões de acesso do usuário ou o código de compartilhamento."
    )
    async def deletar_evento(
        self,
        event_id: str,
        token: Optional[str] = depends.token
    ) -> ApiResponse:

        await self.uow.event_service.deletar_evento(
            event_id=event_id,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=self.request.headers.get('sharing_code')
        )
        await self.uow.commit()
        return ApiResponse(detail="Evento removido com sucesso")


    @router.put(
        "/eventos/{event_id}",
        response_model=ApiResponse,
        summary="Atualizar evento por ID",
        description="Atualiza os detalhes de um evento específico, "
        "verificando as permissões do usuário ou o código de compartilhamento."
    )
    async def atualizar_evento(
        self,
        event_id: str,
        body: EventUpdateRequest,
        token: Optional[str] = depends.token
    ) -> ApiResponse:

        await self.uow.event_service.atualizar_evento(
            event_id=event_id,
            titulo=body.title,
            descricao=body.description,
            inicio=body.start_time,
            fim=body.end_time,
            recorrente=body.is_recurring,
            logged_in_id=await get_logged_in_id(token),
            sharing_code=self.request.headers.get('sharing_code'),
        )
        await self.uow.commit()
        return ApiResponse(detail="Evento atualizado com sucesso")
