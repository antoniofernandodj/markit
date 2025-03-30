from fastapi import APIRouter, HTTPException, status
from src.api import depends
from src.api.schema import ApiResponse, UserCreateRequest, UserUpdateRequest
from fastapi_utils.cbv import cbv
from src.uow import UnityOfWork


router = APIRouter(tags=['User'])


@cbv(router)
class UserController:

    uow: UnityOfWork = depends.uow

    @router.post(
        "/usuarios/",
        response_model=ApiResponse,
        summary="Cadastrar um novo usuário",
        description="Cria um novo usuário com os dados fornecidos, "
        "incluindo nome, email e senha. Em caso de falha na validação, "
        "retorna uma mensagem de erro."
    )
    async def cadastrar_usuario(self, body: UserCreateRequest) -> ApiResponse:

        user = await self.uow.user_service.cadastrar_usuario(
            nome=body.name,
            email=body.email,
            senha=body.password
        )

        await self.uow.commit()
        await self.uow.session.refresh(user)

        return ApiResponse(
            detail="Usuário cadastrado com sucesso!",
            resource={
                'id': user.id,
                'nome': body.name,
                'email': body.email,
            }
        )

    @router.delete(
        "/usuarios/{user_id}",
        response_model=ApiResponse,
        summary="Remover um usuário",
        description="Remove um usuário existente pelo "
        "seu ID. Se o usuário não for encontrado, "
        "retorna um erro 404."
    )
    async def remover_usuario(self, user_id: str) -> ApiResponse:

        user = await self.uow.user_service.repo.get(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado"
            )

        await self.uow.user_service.remover_usuario(user)
        await self.uow.commit()
        return ApiResponse(detail="Usuário removido com sucesso")

    @router.put(
        "/usuarios/{user_id}",
        response_model=ApiResponse,
        summary="Atualizar Cadastro de Usuário",
        description="Atualiza as informações de um usuário, incluindo nome, email e senha,"
        " sendo todos estes campos opcionais. "
        "É necessário fornecer o ID do usuário. O endpoint valida se o usuário existe e, "
        "se o email informado já está em uso por outro usuário. Se a atualização for "
        "bem-sucedida, um retorno de sucesso é enviado."
    )
    async def atualizar_cadastro_de_usuario(self, user_id: str, body: UserUpdateRequest) -> ApiResponse:

        await self.uow.user_service.atualizar_dados_de_usuario(
            user_id=user_id,
            nome=body.name,
            email=body.email,
            senha=body.password
        )
        await self.uow.commit()
        return ApiResponse(detail="Dados de usuario atualizados com sucesso!")
