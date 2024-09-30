from fastapi import APIRouter, HTTPException, status
from typing import Sequence
from src.api import depends
from src.api.schema import SharingCreateRequest, SharingResponse, SharingUpdateRequest


router = APIRouter(tags=['Sharing'])


@router.post(
    "/compartilhamentos/",
    summary="Compartilhar calendário",
    description="Compartilha um calendário com outro usuário, "
    "fornecendo permissões específicas e tornando-o público ou privado."
)
async def compartilhar_calendario(
    request: SharingCreateRequest,
    uow = depends.uow,
):

    calendar = await uow.calendar_service.repo.get(request.calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=404,
            detail="Calendário não encontrado"
        )

    shared_with = await uow.user_service.repo.get(request.shared_with_id)
    if not shared_with:
        raise HTTPException(
            status_code=404,
            detail="Usuário para compartilhar não encontrado"
        )
    
    sharing = await uow.sharing_repository.find_by(
        calendar_id=request.calendar_id,
        shared_with_id=request.shared_with_id
    )

    if sharing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Compartilhamento já existente!"
        )

    sharing = await uow.sharing_service.compartilhar_calendario(
        calendar,
        shared_with,
        request.public,
        request.permissions
    )

    return {
        "detail": "Calendário compartilhado com sucesso!",
        'sharing': request.model_dump()
    }


@router.get(
    "/compartilhamentos/",
    summary="Listar compartilhamentos",
    description="Lista todos os compartilhamentos de um calendário específico, "
    "retornando os usuários com quem foi compartilhado e as permissões concedidas."
)
async def listar_compartilhamentos(
    calendar_id: str,
    uow = depends.uow,
) -> Sequence[SharingResponse]:

    calendar = await uow.calendar_service.repo.get(calendar_id)
    if not calendar:
        raise HTTPException(
            status_code=404,
            detail="Calendário não encontrado"
        )
    
    sharings = await uow.sharing_service.obter_compartilhamentos_por_calendario(
        calendar
    )

    return [sharing.to_pydantic() for sharing in sharings]


@router.delete(
    "/compartilhamentos/{sharing_id}",
    summary="Remover compartilhamento",
    description="Remove um compartilhamento específico pelo ID, "
    "revogando o acesso de um usuário ao calendário."
)
async def deletar_compartilhamento(
    sharing_id: str,
    uow = depends.uow,
):

    sharing = await uow.sharing_service.repo.get(sharing_id)
    if not sharing:
        raise HTTPException(
            status_code=404,
            detail="Compartilhamento não encontrado"
        )
    
    await uow.sharing_service.deletar_compartilhamento(sharing)
    return {"detail": "Compartilhamento removido com sucesso"}


@router.put(
    "/compartilhamentos/{sharing_id}",
    summary="Atualizar um compartilhamento existente",
    description="Este endpoint permite atualizar as permissões e a "
    "visibilidade (pública ou privada) de um compartilhamento existente "
    "com base no ID do compartilhamento. Certifique-se de "
    "fornecer um ID de compartilhamento válido e as novas configurações desejadas."
)
async def atualizar_compartilhamento(
    sharing_id: str,
    body: SharingUpdateRequest,
    uow = depends.uow,
):

    await uow.sharing_service.atualizar_compartilhamento(
        sharing_id=sharing_id,
        permissions=body.permissions,
        public=body.public
    )
    return {"detail": "Compartilhamento atualizado com sucesso"}