from fastapi import APIRouter, HTTPException, status, Request
from typing import Optional

from src.api.schema import EventCreateRequest, EventResponse, EventUpdateRequest
from src.api import depends
from src.api.utils import get_logged_in_id, get_token


router = APIRouter(tags=['Event'])


@router.get(
    "/eventos/{event_id}",
    response_model=EventResponse,
    summary="Obter evento por ID",
    description="Retorna um evento específico pelo ID, verificando "
    "as permissões do usuário logado ou do código de compartilhamento."
)
async def acessar_evento_por_id(
    event_id: str,
    request: Request,
    uow = depends.uow,
):
    token: Optional[str] = get_token(request)

    permissao = await uow.event_service.obter_permissao_de_evento(
        event_id=event_id,
        logged_user_id=await get_logged_in_id(token),
        sharing_code=request.headers.get('sharing_code'),
        permission_type='read'
    )

    if not permissao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação não autorizada!"
        )

    event = await uow.event_repository.get(event_id)
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento não encontrado!"
        )
    
    return event.to_pydantic()


@router.post(
    "/eventos/",
    summary="Cadastrar um novo evento",
    description="Cria um novo evento para o calendário especificado, "
    "desde que o calendário exista."
)
async def cadastrar_evento(
    request: EventCreateRequest,
    uow = depends.uow,
):

    calendar = await uow.calendar_repository.get(request.calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=404,
            detail="Calendário não encontrado"
        )

    await uow.event_service.cadastrar_evento(
        calendar=calendar,
        titulo=request.title,
        descricao=request.description,
        inicio=request.start_time,
        fim=request.end_time,
        recorrente=request.is_recurring
    )

    return {
        "detail": "Evento cadastrado com sucesso!",
        "event": request.model_dump()
    }



@router.delete(
    "/eventos/{event_id}",
    summary="Deletar evento por ID",
    description="Remove um evento específico, verificando as "
    "permissões de acesso do usuário ou o código de compartilhamento."
)
async def deletar_evento(
    event_id: str,
    request: Request,
    uow = depends.uow,
):

    token: Optional[str] = get_token(request)

    permissao = await uow.event_service.obter_permissao_de_evento(
        event_id=event_id,
        logged_user_id=await get_logged_in_id(token),
        sharing_code=request.headers.get('sharing_code'),
        permission_type='write'
    )

    if not permissao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Ação não autorizada!'
        )

    event = await uow.event_service.repo.get(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Evento não encontrado")
    
    await uow.event_service.deletar_evento(event)
    return {"detail": "Evento removido com sucesso"}


@router.put(
    "/eventos/{event_id}",
    summary="Atualizar evento por ID",
    description="Atualiza os detalhes de um evento específico, "
    "verificando as permissões do usuário ou o código de compartilhamento."
)
async def atualizar_evento(
    event_id: str,
    body: EventUpdateRequest,
    request: Request,
    uow = depends.uow,
):

    token: Optional[str] = get_token(request)

    permissao = await uow.event_service.obter_permissao_de_evento(
        event_id=event_id,
        logged_user_id=await get_logged_in_id(token),
        sharing_code=request.headers.get('sharing_code'),
        permission_type='write'
    )

    if not permissao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Ação não autorizada!'
        )

    await uow.event_service.atualizar_evento(
        event_id=event_id,
        titulo=body.title,
        descricao=body.description,
        inicio=body.start_time,
        fim=body.end_time,
        recorrente=body.is_recurring
    )

    return {"detail": "Evento atualizado com sucesso"}
    



"""
Cadastrar User 1 {
    "detail": "Usuário cadastrado com sucesso!",
    "user": {
        0bf168dd-d10d-44fc-98f1-65d68ad3620a
        "name": "user1@example.com",
        "email": "user1@example.com",
        "password": "123456"
    }
}

Cadastrar User 2 {
    "detail": "Usuário cadastrado com sucesso!",
    "user": {
        0cb8b0f4-4cb9-4c0a-8a43-341b8db253f3
        "name": "user2@example.com",
        "email": "user2@example.com",
        "password": "123456"
    }
}

Cadastrar User 3 {
    "detail": "Usuário cadastrado com sucesso!",
    "user": {
        68a9730c-cf55-432a-925c-d1a63e935437
        "name": "user3@example.com",
        "email": "user3@example.com",
        "password": "123456"
    }
}

Cadastrar Calendario 1 {
    "detail": "Calendário cadastrado com sucesso",
    "calendario": {
        a46b3ad1-9d94-4326-b5a6-2c6a15bfddca
        "name": "semana",
        "user_id": "0bf168dd-d10d-44fc-98f1-65d68ad3620a"
    }
}

Cadastrar Evento 1 {
    "detail": "Evento cadastrado com sucesso!",
    "event": {
        f06cd7d2-4f90-4d73-bbab-7c4e631b5636
        "calendar_id": "a46b3ad1-9d94-4326-b5a6-2c6a15bfddca",
        "title": "event1",
        "description": "e1",
        "start_time": "2024-09-30T02:24:01.269000+00:00",
        "end_time": "2025-09-30T02:24:01.269000+00:00",
        "is_recurring": false
    }
}

Cadastrar Evento 2 {
    8837e60a-114d-4ca9-a472-302ef5b2b95d
    "calendar_id": "a46b3ad1-9d94-4326-b5a6-2c6a15bfddca",
    "title": "event2",
    "description": "e2",
    "start_time": "2024-09-30T02:24:01.269Z",
    "end_time": "2025-09-30T02:24:01.269Z",
    "is_recurring": false
}


Gerar compartilhamento para user 2 de calendario 1 {
    228cb55d-1e9f-4b3c-817b-8a3569afdccd
    "detail": "Calendário compartilhado com sucesso!",
    "sharing": {
        "calendar_id": "a46b3ad1-9d94-4326-b5a6-2c6a15bfddca",
        "shared_with_id": "0cb8b0f4-4cb9-4c0a-8a43-341b8db253f3",
        "permissions": "read",
        "public": false
    }
}

acessar calendario 1 Deslogado


acessar calendario 1 como user 1
acessar calendario 1 como user 2
acessar calendario 1 como user 3

editar evento 1 como user 1
editar evento 1 como user 2
editar evento 1 como user 3

remover evento 1 como user 1
remover evento 1 como user 2
remover evento 1 como user 3

"""