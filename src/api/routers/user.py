from fastapi import APIRouter, HTTPException, status
from src.api import depends
from src.api.schema import UserCreateRequest

router = APIRouter(tags=['User'])


@router.post(
    "/usuarios/", 
    summary="Cadastrar um novo usuário",
    description="Cria um novo usuário com os dados fornecidos, incluindo nome, email e senha. Em caso de falha na validação, retorna uma mensagem de erro."
)
async def cadastrar_usuario(
    request: UserCreateRequest,
    uow = depends.uow,
):
    try:
        await uow.user_service.cadastrar_usuario(
            nome=request.name,
            email=request.email,
            senha=request.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "detail": "Usuário cadastrado com sucesso!",
        "user": request.model_dump()
    }


@router.delete(
    "/usuarios/{user_id}", 
    summary="Remover um usuário",
    description="Remove um usuário existente pelo seu ID. Se o usuário não for encontrado, retorna um erro 404."
)
async def remover_usuario(
    user_id: str,
    uow = depends.uow,
):
    user = await uow.user_service.repo.get(user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Usuário não encontrado"
        )
    
    await uow.user_service.remover_usuario(user)
    return {"detail": "Usuário removido com sucesso"}
