from typing_extensions import Optional
from fastapi import APIRouter
from typing import Sequence
from src.api import depends
from src.api.schema import ApiResponse, SharingCreateRequest, SharingResponse, SharingUpdateRequest, SharingsResponse
from fastapi_utils.cbv import cbv

from src.uow import UnityOfWork



router = APIRouter(tags=['Sharing'])


@cbv(router)
class SharingController:

    uow: UnityOfWork = depends.uow

    @router.post(
        "/compartilhamentos/",
        response_model=ApiResponse,
        summary="Compartilhar calendário",
        description="Compartilha um calendário com outro usuário, "
        "fornecendo permissões específicas e tornando-o público ou privado."
    )
    async def compartilhar_calendario(
        self,
        body: SharingCreateRequest
    ) -> ApiResponse:

        sharing = (
            await self.uow.sharing_service.compartilhar_calendario(
                calendar_id=body.calendar_id,
                shared_with_email=body.shared_with_email,
                public=body.public,
                permissions=body.permissions
            )
        )

        await self.uow.commit()
        await self.uow.refresh([sharing])

        return ApiResponse(
            detail="Calendário compartilhado com sucesso!",
            resource={"id": sharing.id}
        )

    @router.get(
        "/compartilhamentos/",
        summary="Listar compartilhamentos",
        response_model=SharingsResponse,
        description="Lista todos os compartilhamentos de um calendário específico, "
        "retornando os usuários com quem foi compartilhado e as permissões concedidas."
    )
    async def listar_compartilhamentos(
        self,
        calendar_id: str,
    ) -> SharingsResponse:

        service = self.uow.sharing_service

        sharings = (
            await service.obter_compartilhamentos_por_calendario(
                calendar_id
            )
        )

        return SharingsResponse(sharings=[SharingResponse.model_validate(sharing) for sharing in sharings])

    @router.delete(
        "/compartilhamentos/{sharing_id}",
        response_model=ApiResponse,
        summary="Remover compartilhamento",
        description="Remove um compartilhamento específico pelo ID, "
        "revogando o acesso de um usuário ao calendário."
    )
    async def deletar_compartilhamento(self, sharing_id: str):
        await self.uow.sharing_service.deletar_compartilhamento(sharing_id)
        await self.uow.commit()
        return ApiResponse(detail="Compartilhamento removido com sucesso")

    @router.put(
        "/compartilhamentos/{sharing_id}",
        response_model=ApiResponse,
        summary="Atualizar um compartilhamento existente",
        description="Este endpoint permite atualizar as permissões e a "
        "visibilidade (pública ou privada) de um compartilhamento existente "
        "com base no ID do compartilhamento. Certifique-se de "
        "fornecer um ID de compartilhamento válido e as novas configurações desejadas."
    )
    async def atualizar_compartilhamento(
        self,
        sharing_id: str,
        body: SharingUpdateRequest
    ) -> ApiResponse:

        await self.uow.sharing_service.atualizar_compartilhamento(
            sharing_id=sharing_id,
            permissions=body.permissions,
            public=body.public
        )

        await self.uow.commit()
        return ApiResponse(detail="Compartilhamento atualizado com sucesso")
