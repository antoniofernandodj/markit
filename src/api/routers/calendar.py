from contextlib import suppress
from fastapi import APIRouter, Depends, HTTPException, Header, status, Request
from typing import Annotated, Optional, Sequence
from src.api import depends
from src.api.schema import CalendarCreateRequest, CalendarResponse
from src.api.security.auth import ApiAuthService
from src.api.utils import get_logged_in_id, get_token


router = APIRouter(tags=['Calendar'])


@router.post(
    "/calendarios/",
    summary='Cadastrar um novo calendário',
    description="Permite cadastrar um novo calendário associado "
    "a um usuário. O usuário deve existir no sistema.",
    status_code=status.HTTP_201_CREATED
)
async def cadastrar_calendario(
    request: CalendarCreateRequest,
    uow = depends.uow
):

    user = await uow.user_service.repo.get(request.user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )

    await uow.calendar_service.cadastrar_calendario(
        request.name, request.public, user
    )

    return {
        "detail": "Calendário cadastrado com sucesso",
        "calendario": request.model_dump()
    }


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
    calendar_id: str,
    request: Request,
    uow = depends.uow
):

    token: Optional[str] = get_token(request)

    permissao = await uow.calendar_service.obter_permissao_de_calendario(
        logged_user_id=await get_logged_in_id(token),
        sharing_code=request.headers.get('sharing_code'),
        calendar_id=calendar_id,
        permission_type='read'
    )

    if not permissao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação não autorizada!"
        )

    calendar = await uow.calendar_service.repo.get(calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=404,
            detail="Calendário não encontrado"
        )

    return calendar.to_pydantic()



@router.get(
    "/calendarios/",
    summary='Listar calendários do usuário logado',
    description='Retorna uma lista de todos os calendários pertencentes '
    'ao usuário logado.',
    status_code=status.HTTP_200_OK
)
async def listar_calendarios(
    current_user = depends.current_user,
    uow = depends.uow
) -> Sequence[CalendarResponse]:

    calendars = (
        await uow.calendar_service.obter_calendarios_por_usuario(
            current_user.get_id()
        )
    )
    if not calendars:
        raise HTTPException(
            status_code=404,
            detail="Nenhum calendário encontrado"
        )

    return [calendar.to_pydantic() for calendar in calendars]


@router.delete(
    "/calendarios/{calendar_id}",
    summary='Deletar um calendário por ID',
    description='Remove um calendário específico pelo seu ID, '
    'verificando as permissões do usuário logado ou do código de '
    'compartilhamento fornecido.',
    status_code=status.HTTP_200_OK
)
async def deletar_calendario(
    calendar_id: str,
    request: Request,
    uow = depends.uow
):
    
    token: Optional[str] = get_token(request)
    
    permissao = await uow.calendar_service.obter_permissao_de_calendario(
        logged_user_id=await get_logged_in_id(token),
        sharing_code=request.headers.get('sharing_code'),
        calendar_id=calendar_id,
        permission_type='write'
    )

    if not permissao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação não autorizada!"
        )

    calendar = await uow.calendar_service.repo.get(calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=404,
            detail="Calendário não encontrado"
        )
    
    await uow.calendar_service.deletar_calendario(calendar)
    return {"detail": "Calendário removido com sucesso"}


@router.put(
    "/calendarios/{calendar_id}",
    summary='Atualizar um calendário por ID',
    description='Atualiza o nome de um calendário específico, '
    'verificando as permissões do usuário logado ou do código '
    'de compartilhamento fornecido.',
    status_code=status.HTTP_200_OK
)
async def atualizar_calendario(
    calendar_id: str,
    name: str,
    request: Request,
    uow = depends.uow
):

    token: Optional[str] = get_token(request)

    permissao = await uow.calendar_service.obter_permissao_de_calendario(
        logged_user_id=await get_logged_in_id(token),
        sharing_code=request.headers.get('sharing_code'),
        calendar_id=calendar_id,
        permission_type='write'
    )

    if not permissao:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ação não autorizada!"
        )

    await uow.calendar_service.atualizar_calendario(
        calendar_id, name
    )

    return {
        "detail": "Calendário atualizado com sucesso"
    }